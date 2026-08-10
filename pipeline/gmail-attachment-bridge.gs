/**
 * Befach Hiring — Gmail → Drive CV bridge  (v3)
 *
 * Claude can read Google Drive but cannot download Gmail attachments. This
 * script is the bridge: it runs in Uday's own Google account, finds document
 * attachments, and copies them into the Drive folder Claude watches.
 *
 * ── INSTALL ───────────────────────────────────────────────────────────────
 *  1. script.google.com — check the avatar top-right is uday.nadiwade@gmail.com
 *  2. Open your project, click in the code, Ctrl+A, Delete, paste this whole
 *     file, Ctrl+S.  (First line must be the /** below — not "function".)
 *  3. Function dropdown → `saveCvAttachments` → Run → approve permissions
 *  4. Function dropdown → `installHourlyTrigger` → Run.  Once, ever.
 *
 * v3: adds .txt (WhatsApp chat exports from WorkIndia carry candidate details)
 *     and widens the noise denylist using what this inbox actually receives.
 */

var TARGET_FOLDER_ID = '1NPR9g7yGVq5ARP3036T_NoRJv7XaCGXd';
var DONE_LABEL = 'Recruitment/CV-Saved';
var LOOKBACK_DAYS = 90;
var MAX_THREADS = 150;

/** Attachment types worth saving. */
var DOC_TYPES = [
  'text/plain',
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/rtf',
  'application/zip',
  'application/x-zip-compressed'
];

/**
 * Senders that mail documents constantly and never mail job applications.
 * This is the only filter; it exists to keep broker notes and fund mailers
 * out of the CV folder. Add to it whenever noise gets through.
 */
var NOISE = [
  // brokers, exchanges, depositories
  'zerodha.net', 'reportsmailer', 'shoonya.com', 'bseindia.in', 'bseindia.com',
  'nse.co.in', 'mcxindia.com', 'nsdl.co.in', 'cdslindia.com',
  // banks, funds, registrars
  'icici.bank.in', 'camsonline.com', 'kfintech.com', 'sundarammutual.com',
  'wealthcompany.in', 'policybazaar.com', 'careinsurance.com',
  // government, utilities, vendors
  'incometax.gov.in', 'zoom.us', 'anthropic.com', 'jio.com', 'airtel.com',
  'wetrade.org', 'iiflcapital.com', 'dcal.co.in', 'alilokhandwalaofficial.com',
  // job-board marketing (not applicants)
  'linkedin.com', 'indeed.com', 'internshala.com', 'unstop.news',
  // generic no-reply patterns
  'newsletters-noreply', 'notifications-noreply', 'messages-noreply',
  'groups-noreply', 'invoice+statements', 'donotreply', 'estatement',
  'no-reply-margin', 'no-reply-contract', 'no-reply-account'
];

// ── Diagnostic ──────────────────────────────────────────────────────────────

function diagnose() {
  Logger.log('=== BEFACH CV BRIDGE v3 — DIAGNOSTIC ===');

  try {
    Logger.log('Running as: ' + Session.getEffectiveUser().getEmail());
  } catch (e) {
    Logger.log('Running as: unknown (' + e + ')');
  }

  try {
    var folder = DriveApp.getFolderById(TARGET_FOLDER_ID);
    var files = folder.getFiles();
    var n = 0;
    while (files.hasNext()) { files.next(); n++; }
    Logger.log('Drive folder OK: "' + folder.getName() + '" — ' + n + ' files');
  } catch (e) {
    Logger.log('DRIVE FOLDER FAILED: ' + e);
    Logger.log('--> Wrong Google account, or no access to that folder.');
    return;
  }

  var threads = GmailApp.search('has:attachment newer_than:' + LOOKBACK_DAYS + 'd', 0, 20);
  Logger.log('Sample of 20 threads with attachments:');

  for (var i = 0; i < threads.length && i < 10; i++) {
    var msgs = threads[i].getMessages();
    for (var j = 0; j < msgs.length; j++) {
      var atts = msgs[j].getAttachments();
      for (var k = 0; k < atts.length; k++) {
        Logger.log('  from=' + msgs[j].getFrom() +
                   ' | file=' + atts[k].getName() +
                   ' | type=' + atts[k].getContentType() +
                   ' | noise=' + isNoise(String(msgs[j].getFrom()).toLowerCase()) +
                   ' | willSave=' + (DOC_TYPES.indexOf(atts[k].getContentType()) !== -1));
      }
    }
  }
  Logger.log('=== END ===');
}

// ── Main ────────────────────────────────────────────────────────────────────

function saveCvAttachments() {
  var folder = DriveApp.getFolderById(TARGET_FOLDER_ID);
  var doneLabel = GmailApp.getUserLabelByName(DONE_LABEL) ||
                  GmailApp.createLabel(DONE_LABEL);

  var query = 'has:attachment newer_than:' + LOOKBACK_DAYS + 'd -label:' + DONE_LABEL;
  var threads = GmailApp.search(query, 0, MAX_THREADS);
  var saved = 0;

  for (var t = 0; t < threads.length; t++) {
    var messages = threads[t].getMessages();

    for (var m = 0; m < messages.length; m++) {
      var msg = messages[m];
      if (isNoise(String(msg.getFrom() || '').toLowerCase())) { continue; }

      var attachments = msg.getAttachments();
      for (var a = 0; a < attachments.length; a++) {
        var att = attachments[a];
        if (DOC_TYPES.indexOf(att.getContentType()) === -1) { continue; }
        if (att.getSize() > 20 * 1024 * 1024) { continue; }

        var filename = buildFilename(msg, att);
        if (folder.getFilesByName(filename).hasNext()) { continue; }

        folder.createFile(att.copyBlob()).setName(filename);
        saved++;
        Logger.log('Saved: ' + filename);
      }
    }
    threads[t].addLabel(doneLabel);
  }

  Logger.log('Threads examined: ' + threads.length + ' | files saved: ' + saved);
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function isNoise(from) {
  for (var i = 0; i < NOISE.length; i++) {
    if (from.indexOf(NOISE[i]) !== -1) { return true; }
  }
  return false;
}

/**
 * Sender and date go into the filename — Claude sees the file in Drive with no
 * link back to the email, so the name has to carry that context.
 */
function buildFilename(msg, att) {
  var date = Utilities.formatDate(msg.getDate(),
                                  Session.getScriptTimeZone(), 'yyyy-MM-dd');
  var email = (String(msg.getFrom() || '').match(/[\w.+-]+@[\w.-]+\.\w+/) ||
               ['unknown'])[0];
  var clean = att.getName().replace(/[\\\/:*?"<>|]/g, '-');
  return date + '__' + email + '__' + clean;
}

// ── Run once ────────────────────────────────────────────────────────────────

function installHourlyTrigger() {
  var existing = ScriptApp.getProjectTriggers();
  for (var i = 0; i < existing.length; i++) {
    if (existing[i].getHandlerFunction() === 'saveCvAttachments') {
      ScriptApp.deleteTrigger(existing[i]);
    }
  }
  ScriptApp.newTrigger('saveCvAttachments').timeBased().everyHours(1).create();
  Logger.log('Hourly trigger installed.');
}

/** Forces a full re-scan on the next run. */
function resetProcessedLabel() {
  var label = GmailApp.getUserLabelByName(DONE_LABEL);
  if (!label) { Logger.log('Label does not exist — script has never run.'); return; }
  var threads = label.getThreads(0, 400);
  for (var i = 0; i < threads.length; i++) { threads[i].removeLabel(label); }
  Logger.log('Cleared label from ' + threads.length + ' threads.');
}
