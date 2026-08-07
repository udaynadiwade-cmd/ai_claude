/**
 * Befach Hiring — Gmail → Drive CV bridge
 *
 * Why this exists: the hiring agent can read Google Drive but cannot download
 * Gmail attachments. This script closes that gap. It finds likely job
 * applications in Gmail, saves their CV attachments into a Drive folder the
 * agent watches, and labels the thread so it is never processed twice.
 *
 * SETUP (once, ~3 minutes)
 *   1. Go to script.google.com → New project. Name it "Befach CV Bridge".
 *   2. Delete the placeholder code. Paste this whole file in. Save.
 *   3. Run → select `saveCvAttachments` → Run.
 *      Google will ask for permission to read Gmail and write Drive. Approve.
 *      ("Advanced" → "Go to Befach CV Bridge (unsafe)" is normal for your own
 *       scripts — this one is not published or verified by Google.)
 *   4. Run → select `installHourlyTrigger` → Run. Once only.
 *      It now runs by itself every hour, forever.
 *
 * To check it later: script.google.com → your project → Executions.
 */

// ── Configuration ───────────────────────────────────────────────────────────

/** Drive folder the hiring agent watches. */
var TARGET_FOLDER_ID = '1NPR9g7yGVq5ARP3036T_NoRJv7XaCGXd';

/** Applied to threads already handled, so nothing is saved twice. */
var DONE_LABEL = 'Recruitment/CV-Saved';

/** How far back to look. 14 days catches anything missed during downtime. */
var LOOKBACK = 'newer_than:14d';

/** Attachment types worth saving. */
var ALLOWED_TYPES = [
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/rtf',
  'application/zip'
];

/**
 * Senders that send attachments constantly and never send job applications.
 * This is what keeps bank statements and broker notes out of the CV folder.
 * Add to it whenever noise slips through.
 */
var NOISE_SENDERS = [
  'zerodha.net', 'icici.bank.in', 'camsonline.com', 'kfintech.com',
  'incometax.gov.in', 'nse.co.in', 'bseindia.com', 'zoom.us',
  'linkedin.com', 'indeed.com', 'internshala.com', 'unstop.news',
  'policybazaar.com', 'careinsurance.com', 'sundarammutual.com',
  'wealthcompany.in', 'anthropic.com', 'jio.com', 'airtel.com',
  'noreply', 'no-reply', 'donotreply', 'do-not-reply'
];

/** Words that suggest an actual application. */
var APPLICATION_HINTS = [
  'resume', 'cv', 'curriculum vitae', 'application', 'applying', 'apply',
  'job', 'position', 'vacancy', 'opening', 'candidature', 'hiring',
  'opportunity', 'interested in', 'my profile'
];

// ── Main ────────────────────────────────────────────────────────────────────

function saveCvAttachments() {
  var folder = DriveApp.getFolderById(TARGET_FOLDER_ID);
  var doneLabel = GmailApp.getUserLabelByName(DONE_LABEL) ||
                  GmailApp.createLabel(DONE_LABEL);

  var query = 'has:attachment ' + LOOKBACK + ' -label:' + DONE_LABEL;
  var threads = GmailApp.search(query, 0, 100);

  var saved = 0, skipped = 0;

  for (var t = 0; t < threads.length; t++) {
    var thread = threads[t];
    var messages = thread.getMessages();
    var savedFromThread = false;

    for (var m = 0; m < messages.length; m++) {
      var msg = messages[m];
      var from = String(msg.getFrom() || '').toLowerCase();

      if (isNoise(from)) { continue; }

      var haystack = (msg.getSubject() + ' ' + msg.getPlainBody()).toLowerCase();
      var attachments = msg.getAttachments();

      for (var a = 0; a < attachments.length; a++) {
        var att = attachments[a];
        if (ALLOWED_TYPES.indexOf(att.getContentType()) === -1) { continue; }
        if (att.getSize() > 15 * 1024 * 1024) { continue; }

        var name = att.getName().toLowerCase();
        var looksLikeCv = mentionsApplication(haystack) ||
                          mentionsApplication(name);
        if (!looksLikeCv) { skipped++; continue; }

        var filename = buildFilename(msg, att);
        if (alreadyInFolder(folder, filename)) { continue; }

        folder.createFile(att.copyBlob()).setName(filename);
        saved++;
        savedFromThread = true;
      }
    }

    // Label the thread either way, so it is examined exactly once.
    thread.addLabel(doneLabel);
    if (savedFromThread) { thread.addLabel(recruitmentLabel()); }
  }

  Logger.log('Threads examined: ' + threads.length +
             ' | CVs saved: ' + saved +
             ' | attachments skipped: ' + skipped);
}

// ── Helpers ─────────────────────────────────────────────────────────────────

function isNoise(from) {
  for (var i = 0; i < NOISE_SENDERS.length; i++) {
    if (from.indexOf(NOISE_SENDERS[i]) !== -1) { return true; }
  }
  return false;
}

function mentionsApplication(text) {
  for (var i = 0; i < APPLICATION_HINTS.length; i++) {
    if (text.indexOf(APPLICATION_HINTS[i]) !== -1) { return true; }
  }
  return false;
}

/**
 * Encodes who sent it and when into the filename, because the agent reads
 * Drive without seeing the originating email.
 */
function buildFilename(msg, att) {
  var date = Utilities.formatDate(msg.getDate(),
                                  Session.getScriptTimeZone(), 'yyyy-MM-dd');
  var from = String(msg.getFrom() || '');
  var email = (from.match(/[\w.+-]+@[\w.-]+\.\w+/) || ['unknown'])[0];
  var clean = att.getName().replace(/[\\\/:*?"<>|]/g, '-');
  return date + '__' + email + '__' + clean;
}

function alreadyInFolder(folder, filename) {
  return folder.getFilesByName(filename).hasNext();
}

function recruitmentLabel() {
  return GmailApp.getUserLabelByName('Recruitment') ||
         GmailApp.createLabel('Recruitment');
}

// ── Trigger installation — run once ─────────────────────────────────────────

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

/**
 * Undo helper: removes the Recruitment/CV-Saved label from everything so the
 * next run re-examines the last 14 days. Use if the filters were tuned and
 * you want a second pass.
 */
function resetProcessedLabel() {
  var label = GmailApp.getUserLabelByName(DONE_LABEL);
  if (!label) { return; }
  var threads = label.getThreads(0, 200);
  for (var i = 0; i < threads.length; i++) {
    threads[i].removeLabel(label);
  }
  Logger.log('Cleared label from ' + threads.length + ' threads.');
}
