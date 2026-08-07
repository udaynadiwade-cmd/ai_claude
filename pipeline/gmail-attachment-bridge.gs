/**
 * Befach Hiring — Gmail → Drive CV bridge  (v2, simplified)
 *
 * WHY: Claude can read Google Drive but cannot download Gmail attachments —
 * no such capability exists. This script is the bridge. Install once; after
 * that every CV that arrives by email lands in Drive on its own and Claude
 * does the rest. There is no per-resume manual step.
 *
 * v2 changes: filtering removed. This script now saves every document
 * attachment that isn't from a known-noise sender, and Claude decides what is
 * and isn't a CV when it reads them. Fewer moving parts, fewer silent skips.
 *
 * ── SETUP ─────────────────────────────────────────────────────────────────
 *  1. script.google.com  ← make sure the avatar top-right is uday.nadiwade@gmail.com
 *  2. New project → delete the sample code → paste this whole file → Save
 *  3. Function dropdown → `diagnose` → Run → approve permissions
 *     → open "Execution log" and send Uday's Claude session what it printed
 *  4. If diagnose looks right: Function dropdown → `installHourlyTrigger` → Run
 *
 * That's it. It now runs by itself every hour.
 */

var TARGET_FOLDER_ID = '1NPR9g7yGVq5ARP3036T_NoRJv7XaCGXd';
var DONE_LABEL = 'Recruitment/CV-Saved';
var LOOKBACK_DAYS = 90;   // generous on first run; harmless afterwards
var MAX_THREADS = 150;

var DOC_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/rtf',
  'application/zip',
  'application/x-zip-compressed'
];

/**
 * Senders that mail documents constantly and never mail job applications.
 * This is the only filter left, and it exists purely to stop the folder
 * filling with bank statements and broker notes.
 */
var NOISE = [
  'zerodha.net', 'icici.bank.in', 'camsonline.com', 'kfintech.com',
  'incometax.gov.in', 'nse.co.in', 'bseindia.com', 'zoom.us',
  'policybazaar.com', 'careinsurance.com', 'sundarammutual.com',
  'wealthcompany.in', 'anthropic.com', 'jio.com', 'airtel.com',
  'wetrade.org', 'iiflcapital.com', 'dcal.co.in',
  'newsletters-noreply', 'notifications-noreply', 'messages-noreply',
  'groups-noreply', 'invoice+statements', 'no-reply-margin',
  'no-reply-contract', 'donotreply', 'estatement'
];

// ── Diagnostic — run this FIRST ─────────────────────────────────────────────

function diagnose() {
  Logger.log('=== BEFACH CV BRIDGE — DIAGNOSTIC ===');

  try {
    Logger.log('Running as: ' + Session.getEffectiveUser().getEmail());
  } catch (e) {
    Logger.log('Running as: could not determine (' + e + ')');
  }

  try {
    var folder = DriveApp.getFolderById(TARGET_FOLDER_ID);
    Logger.log('Drive folder OK: "' + folder.getName() + '"');
    var files = folder.getFiles();
    var n = 0;
    while (files.hasNext()) { files.next(); n++; }
    Logger.log('Files currently in folder: ' + n);
  } catch (e) {
    Logger.log('DRIVE FOLDER FAILED: ' + e);
    Logger.log('--> Wrong Google account, or no access to that folder.');
    return;
  }

  var query = 'has:attachment newer_than:' + LOOKBACK_DAYS + 'd';
  var threads = GmailApp.search(query, 0, 20);
  Logger.log('Gmail threads with attachments (sample of 20): ' + threads.length);

  for (var i = 0; i < threads.length && i < 10; i++) {
    var msgs = threads[i].getMessages();
    for (var j = 0; j < msgs.length; j++) {
      var atts = msgs[j].getAttachments();
      for (var k = 0; k < atts.length; k++) {
        Logger.log('  from=' + msgs[j].getFrom() +
                   ' | file=' + atts[k].getName() +
                   ' | type=' + atts[k].getContentType() +
                   ' | noise=' + isNoise(String(msgs[j].getFrom()).toLowerCase()) +
                   ' | docType=' + (DOC_TYPES.indexOf(atts[k].getContentType()) !== -1));
      }
    }
  }
  Logger.log('=== END DIAGNOSTIC ===');
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
 * Sender and date go into the filename: Claude sees the file in Drive with no
 * link back to the email it came from, so the name has to carry that context.
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
