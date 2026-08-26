/**
 * Playwright script: Find recruiting agencies in Hyderabad
 * Searches for agency contact information and extracts emails
 * Outputs to: out/recruit-agencies.csv
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const outDir = path.join(__dirname, '../../out');
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}

const csvPath = path.join(outDir, 'recruit-agencies.csv');

async function main() {
  console.log('Starting recruiting agency search...');
  const browser = await chromium.launch();
  const page = await browser.newPage();

  const agencies = new Set(); // Use Set to avoid duplicates
  const agencies_list = [];

  try {
    // Search Google for recruiting agencies in Hyderabad
    console.log('Searching for recruiting agencies in Hyderabad...');
    await page.goto('https://www.google.com/search?q=recruitment+agencies+Hyderabad+India+contact+email', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    // Extract search results
    const results = await page.locator('div.g').all();
    console.log(`Found ${results.length} search results`);

    for (let i = 0; i < Math.min(results.length, 10); i++) {
      try {
        const titleEl = await results[i].locator('h3').first();
        const title = await titleEl.textContent().catch(() => '');

        const linkEl = await results[i].locator('a').first();
        const link = await linkEl.getAttribute('href').catch(() => '');

        if (title && link && !link.includes('google.com')) {
          const agency = { name: title.trim(), website: link, email: '' };

          // Try to extract email from snippet
          const snippetEl = await results[i].locator('span[style*="color"]').first();
          const snippet = await snippetEl.textContent().catch(() => '');

          // Look for email pattern in snippet or title
          const emailMatch = snippet.match(/[\w\.-]+@[\w\.-]+\.\w+/);
          if (emailMatch) {
            agency.email = emailMatch[0];
          }

          const agencyKey = agency.name.toLowerCase();
          if (!agencies.has(agencyKey)) {
            agencies.add(agencyKey);
            agencies_list.push(agency);
            console.log(`Found: ${agency.name} - ${agency.email || 'no email in snippet'}`);
          }
        }
      } catch (err) {
        console.log(`Error processing result ${i}:`, err.message);
      }
    }

    // Try searching on specific recruitment directories
    console.log('\nSearching recruitment directories...');

    // Search on JustDial
    try {
      await page.goto('https://www.justdial.com/Hyderabad/Recruitment-Consultants/nctx-1-1-pgi', {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      const justdialAgencies = await page.locator('a.rst-cont-name').all();
      console.log(`Found ${justdialAgencies.length} on JustDial`);

      for (let i = 0; i < Math.min(justdialAgencies.length, 5); i++) {
        try {
          const name = await justdialAgencies[i].textContent();
          const agencyKey = name.toLowerCase().trim();

          if (!agencies.has(agencyKey)) {
            agencies.add(agencyKey);
            agencies_list.push({ name: name.trim(), website: '', email: '' });
            console.log(`Added from JustDial: ${name}`);
          }
        } catch (err) {
          console.log(`Error on JustDial item:`, err.message);
        }
      }
    } catch (err) {
      console.log('JustDial search error:', err.message);
    }

  } catch (err) {
    console.error('Error during search:', err);
  } finally {
    await browser.close();
  }

  // Write CSV
  console.log(`\nWriting ${agencies_list.length} agencies to CSV...`);

  let csv = 'Agency Name,Website,Email,Date Added\n';
  const today = new Date().toISOString().split('T')[0];

  agencies_list.forEach(agency => {
    const name = (agency.name || '').replace(/"/g, '""');
    const website = agency.website || '';
    const email = agency.email || '';
    csv += `"${name}","${website}","${email}","${today}"\n`;
  });

  fs.writeFileSync(csvPath, csv);
  console.log(`✓ Results saved to: ${csvPath}`);
  console.log(`Total agencies found: ${agencies_list.length}`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
