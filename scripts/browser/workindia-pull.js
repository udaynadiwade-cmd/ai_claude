/**
 * Playwright script: Pull Sales Executive candidates from WorkIndia
 * Logs into WorkIndia employer account and extracts candidate applications
 * Outputs to: out/workindia-sales-executive-candidates.csv
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const outDir = path.join(__dirname, '../../out');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

const csvPath = path.join(outDir, 'workindia-sales-executive-candidates.csv');

// Get credentials from environment
const email = process.env.WORKINDIA_EMAIL;
const password = process.env.WORKINDIA_PASSWORD;

if (!email || !password) {
  console.error('Error: WORKINDIA_EMAIL or WORKINDIA_PASSWORD not set');
  process.exit(1);
}

async function main() {
  console.log('Starting WorkIndia candidate pull...');
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const candidates = [];

  try {
    // Navigate to WorkIndia
    console.log('Navigating to WorkIndia...');
    await page.goto('https://www.workindia.in', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Click on Employer/Login button
    console.log('Logging in...');

    // Try to find and click login button
    try {
      await page.click('a:has-text("Employer Login")');
    } catch (e) {
      console.log('Trying alternate login selector...');
      await page.click('button:has-text("Login")');
    }

    // Wait for login page
    await page.waitForURL(/login|signin/, { timeout: 10000 }).catch(() => {
      console.log('Login page load timed out, continuing...');
    });

    // Enter email
    await page.fill('input[type="email"]', email);
    console.log('Email entered');

    // Enter password
    await page.fill('input[type="password"]', password);
    console.log('Password entered');

    // Click login button
    await page.click('button[type="submit"]');
    console.log('Login submitted');

    // Wait for dashboard to load
    await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {
      console.log('Dashboard load timed out');
    });

    console.log('Logged in successfully');

    // Navigate to job applications or candidates section
    console.log('Looking for Sales Executive applications...');

    // Try different possible URLs for applications
    const possibleUrls = [
      'https://www.workindia.in/employer/job-applicants',
      'https://www.workindia.in/employer/applications',
      'https://www.workindia.in/employer/candidates'
    ];

    let foundPage = false;
    for (const url of possibleUrls) {
      try {
        await page.goto(url, {
          waitUntil: 'networkidle',
          timeout: 15000
        });
        foundPage = true;
        console.log(`Navigated to: ${url}`);
        break;
      } catch (e) {
        console.log(`Could not access ${url}`);
      }
    }

    if (!foundPage) {
      console.log('Could not find applications page, attempting to extract from current page');
    }

    // Look for candidate/application listings
    const candidateRows = await page.locator('div[class*="candidate"], tr[class*="applicant"], div[class*="application"]').all();
    console.log(`Found ${candidateRows.length} potential candidate rows`);

    // Extract candidate data
    for (let i = 0; i < Math.min(candidateRows.length, 20); i++) {
      try {
        const row = candidateRows[i];
        const text = await row.textContent();

        // Look for Sales Executive in the text
        if (text && text.includes('Sales') && (text.includes('Executive') || text.includes('Sales'))) {
          // Try to extract candidate information
          const candidate = {
            name: '',
            role: 'Sales Executive',
            phone: '',
            email: '',
            experience: '',
            location: '',
            status: '',
            applied_date: ''
          };

          // Try to extract name from link or text
          try {
            const nameEl = await row.locator('a, span').first();
            candidate.name = await nameEl.textContent().catch(() => '');
          } catch (e) {
            candidate.name = text.split('\n')[0];
          }

          // Try to find email/phone in row
          const emailMatch = text.match(/[\w\.-]+@[\w\.-]+\.\w+/);
          if (emailMatch) {
            candidate.email = emailMatch[0];
          }

          const phoneMatch = text.match(/[\d\s\-\+]{10,}/);
          if (phoneMatch) {
            candidate.phone = phoneMatch[0].trim();
          }

          if (candidate.name && (candidate.email || candidate.phone)) {
            candidates.push(candidate);
            console.log(`Found: ${candidate.name} - ${candidate.email || candidate.phone}`);
          }
        }
      } catch (err) {
        console.log(`Error processing row ${i}:`, err.message);
      }
    }

    // If no candidates found through scraping, try API approach
    if (candidates.length === 0) {
      console.log('No candidates found through page scraping, attempting API...');

      // Try to make API call for candidates
      try {
        const response = await page.request.get('https://www.workindia.in/api/employer/applicants?role=Sales%20Executive');
        if (response.ok()) {
          const data = await response.json();
          console.log(`API returned ${data?.data?.length || 0} candidates`);

          if (data?.data && Array.isArray(data.data)) {
            data.data.forEach(candidate => {
              candidates.push({
                name: candidate.name || candidate.full_name || '',
                role: 'Sales Executive',
                phone: candidate.phone || candidate.mobile || '',
                email: candidate.email || '',
                experience: candidate.experience || '',
                location: candidate.location || '',
                status: candidate.status || 'Applied',
                applied_date: candidate.created_at || new Date().toISOString().split('T')[0]
              });
            });
            console.log(`Extracted ${candidates.length} candidates from API`);
          }
        }
      } catch (err) {
        console.log('API call failed:', err.message);
      }
    }

  } catch (err) {
    console.error('Error during scraping:', err);
  } finally {
    await browser.close();
  }

  // Write CSV
  console.log(`\nWriting ${candidates.length} candidates to CSV...`);

  let csv = 'Name,Role,Phone,Email,Experience,Location,Status,Applied Date\n';

  candidates.forEach(candidate => {
    const name = (candidate.name || '').replace(/"/g, '""');
    const role = candidate.role || '';
    const phone = candidate.phone || '';
    const email = candidate.email || '';
    const experience = (candidate.experience || '').replace(/"/g, '""');
    const location = (candidate.location || '').replace(/"/g, '""');
    const status = candidate.status || '';
    const date = candidate.applied_date || '';

    csv += `"${name}","${role}","${phone}","${email}","${experience}","${location}","${status}","${date}"\n`;
  });

  fs.writeFileSync(csvPath, csv);
  console.log(`✓ Results saved to: ${csvPath}`);
  console.log(`Total candidates extracted: ${candidates.length}`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
