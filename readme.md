<div align="center">

<img src="logo.ico" width="120" alt="MTA Assistant Logo" />

<h1>🎮 MTA Assistant</h1>

<p><strong>A powerful Windows utility for MTA:SA players — built with PySide6.</strong></p>

<p>
  <img src="https://img.shields.io/badge/version-1.14.0-blue?style=for-the-badge" alt="Version" />
  <img src="https://img.shields.io/badge/platform-Windows-0078D6?style=for-the-badge&logo=windows" alt="Platform" />
  <img src="https://img.shields.io/badge/python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/made%20by-AmooReza-e74c3c?style=for-the-badge" alt="Made By" />
</p>

<p><strong>Calculate work reports · Compress screenshots · Manage factions · Sub-Leaders tools — all in one place.</strong></p>

</div>

<hr>

<h2>🎬 Video Tutorial</h2>

<p>Watch a quick walkthrough of MTA Assistant in action — from setup to creating your first work report.</p>

<div align="center">

  <a href="https://www.aparat.com/v/dus4h5a" target="_blank">
    <img src="https://www.aparat.com/video/video/thumbnail/videohash/dus4h5a" alt="MTA Assistant Video Tutorial" width="720" />
  </a>

  <br><br>

  <a href="https://www.aparat.com/v/dus4h5a" target="_blank">
    <strong>▶  Watch on Aparat</strong>
  </a>

</div>

<hr>

<h2>✨ Features</h2>

<h3>🧙 First-Time Setup Wizard</h3>
<p>New users get a clean <strong>4-step wizard</strong> on first launch: MTA folder → Faction → Rank → Profile &amp; theme. Everything is validated, and you can go back and forth between steps.</p>

<h3>👁️ Preview Before Creating</h3>
<p>Before starting, a <strong>preview dialog</strong> shows the faction, screenshots count, current PNG size, compression level, <strong>estimated output size</strong>, and <strong>free disk space</strong> with color-coded warnings.</p>

<h3>🛡️ Disk Space Check</h3>
<p>If there isn't enough free space on the Desktop drive, the app warns you <strong>before</strong> starting — no more half-finished reports.</p>

<h3>🎚️ Adjustable Compression Level</h3>
<p>Choose how aggressively screenshots get compressed in <strong>Settings</strong>: <strong>250 KB</strong> (default), <strong>200 KB</strong>, or <strong>150 KB</strong> per image. Your choice is remembered forever.</p>

<h3>📁 Create Missing Category Folders</h3>
<p>A tool to <strong>auto-create any missing category folders</strong> for your current faction. Existing folders are never touched.</p>

<h3>🔄 Auto-Update</h3>
<p>Checks for updates automatically every time you launch. If a newer version is available, a clean dialog lets you download it with one click — or skip that specific version. Manual check is also available from <strong>Help → Check for Updates...</strong></p>

<h3>📊 Work Report Calculator</h3>
<p>Automatically counts your screenshots across all category folders and calculates your total earnings per category — with <strong>faction-specific pricing</strong> applied instantly.</p>

<h3>📦 One-Click Work Report Creation</h3>
<p>Converts every PNG screenshot to a compressed JPG, packs them into a clean folder structure on your Desktop, and automatically zips everything — with a <strong>live progress bar and ETA</strong> so the app never freezes.</p>

<h3>📤 Export Reports to CSV &amp; PDF</h3>
<p>Save your work report as a shareable file — no more screenshots of the table. Export directly to:</p>
<ul>
  <li><strong>CSV</strong> — opens in Excel / Google Sheets with proper encoding</li>
  <li><strong>PDF</strong> — professional layout ready to send to your faction admin</li>
</ul>

<h3>👮 Sub-Leaders Panel <em>(for every faction)</em></h3>
<p>A dedicated panel available for <strong>all factions</strong> with two tabs — <strong>TEST</strong> and <strong>FP Calculator</strong>. The sections inside the TEST tab adapt to your current faction automatically:</p>

<table>
  <thead>
    <tr>
      <th align="left">Section</th>
      <th align="center">Police Department</th>
      <th align="center">Other Factions</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Player Name + <strong>Copy Start Test Message</strong></td>
      <td align="center">✅</td>
      <td align="center">❌</td>
    </tr>
    <tr>
      <td><strong>Editable Question List</strong> (Copy / Edit / Delete)</td>
      <td align="center">✅</td>
      <td align="center">✅</td>
    </tr>
    <tr>
      <td><strong>Accept / Reject / Log&nbsp;/d</strong> with AV Count</td>
      <td align="center">✅</td>
      <td align="center">❌</td>
    </tr>
  </tbody>
</table>

<ul>
  <li>
    <strong>TEST</strong> — paste a player's name and click <strong>Copy Start Test Message</strong> to auto-fill the formatted start-test message with the player's name. Use the <strong>Accept</strong>, <strong>Reject</strong>, and <strong>Log&nbsp;/d</strong> buttons (with AV count selection) to copy the standard PD test-flow messages.
    <br>
    👉 The question list is <strong>fully editable</strong>: add, edit, or delete questions per faction. Each question gets its own <strong>Copy / Edit / Delete</strong> row. Changes are saved automatically in <code>%APPDATA%\MTA Assistant\test_questions.json</code> and remembered per faction.
  </li>
  <li>
    <strong>FP Calculator</strong> — automatically computes a player's FP based on rank, FW count, and special conditions (Outlaw, insulting the leader, 2 FWs in the first week, 4+ total FWs, early resignation). Direct-kick cases override the rank-based calculation.
  </li>
</ul>
<p>Switching faction in Settings updates the panel <strong>instantly</strong> — no restart needed.</p>

<h3>🚔 Fine Calculator <em>(Police Department only)</em></h3>
<p>Enter a driver's speed and choose a location (LS City, LV City, SF City, Heavy Traffic, Highway) to instantly compute the fine:</p>
<p align="center"><code>$5,000 base + $2,000 per 20 KM/H over the limit</code></p>

<h3>📊 Faction Stats Dashboard</h3>
<p>A visual dashboard with:</p>
<ul>
  <li>Total screenshots count</li>
  <li>Total amount earned</li>
  <li>Number of active categories</li>
  <li>Top category by count</li>
  <li>Color-coded bar chart breakdown per category</li>
</ul>

<h3>🔒 Offline License System</h3>
<p>15-day free trial with <strong>Ed25519 offline license verification</strong>. Once activated, license information and remaining days are always visible in the status bar and the Home / Settings pages — no internet needed. Tamper detection (clock rollback, HWID mismatch) protects against trivial bypasses.</p>

<h3>🌙 Dark Mode</h3>
<p>Switch between <strong>Light</strong> and <strong>Dark</strong> themes with a single click. Your choice is saved in the Windows registry and applied instantly.</p>

<h3>🖼️ Screenshot Preview</h3>
<p>Double-click any row in the work report table to open a gallery of that category's screenshots. Double-click a thumbnail to open the original file in your default viewer.</p>

<h3>🚓 Nine Factions Supported</h3>
<p>Choose your faction and the app applies the correct price list automatically:</p>
<ul>
  <li>👮 <strong>Police Department</strong></li>
  <li>🚔 <strong>Police Federal</strong></li>
  <li>🪖 <strong>National Guard</strong></li>
  <li>🚕 <strong>Taxi</strong> <em>(rank-based)</em></li>
  <li>🎯 <strong>Hitman Agency</strong> <em>(rank-based)</em></li>
  <li>🚑 <strong>Medic</strong> <em>(rank-based)</em></li>
  <li>🎓 <strong>School Instructor</strong> <em>(coming soon)</em></li>
  <li>📰 <strong>New Reporter</strong> <em>(rank-based)</em></li>
  <li>🔧 <strong>Mechanic</strong> <em>(coming soon)</em></li>
</ul>

<h3>🎚️ Rank-Based Pricing</h3>
<p>Rank-based factions (Taxi, Hitman Agency, Medic, New Reporter) support <strong>5 ranks</strong>, each with its own price list. Pick your rank once — it's remembered forever.</p>

<h3>🔤 Case-Insensitive Folder Matching</h3>
<p>Folder names no longer need to match exactly. Whether your folders are named <code>arrest</code>, <code>ARREST</code>, or <code>Arrest</code> — the app treats them all the same. Same goes for <code>Slot-Gun</code>, <code>towcar</code>, and every other category.</p>

<h3>💾 Registry Persistence</h3>
<p>Your MTA:SA folder, faction, rank, in-game name, theme, compression level, license key, and trial status are saved in the Windows registry. <strong>No setup needed on subsequent launches.</strong></p>

<h3>🧹 Clear Work Reports</h3>
<p>Clean out all screenshot folders in one click — with a confirmation dialog for safety.</p>

<h3>🎨 Modern UI</h3>
<p>Clean, modern interface built with PySide6 and custom QSS styling. No ugly default widgets.</p>

<h3>🔒 Admin Rights</h3>
<p>The standalone <code>.exe</code> automatically requests admin elevation on launch — no manual right-click needed.</p>

<hr>

<h2>📥 Download</h2>
<p>Grab the latest <strong><code>MTA Assistant.exe</code></strong> from the <a href="https://github.com/ZvanTors/MTA-Assistant/releases"><strong>Releases</strong></a> page.</p>
<blockquote>
  <p>⚠️ <strong>Windows SmartScreen Warning:</strong> Since the exe is unsigned, Windows may warn you the first time. Click <strong>More info → Run anyway</strong>.</p>
</blockquote>

<hr>

<h2>🚀 Quick Start</h2>
<ol>
  <li><strong>Download</strong> <code>MTA Assistant.exe</code> from the Releases page.</li>
  <li><strong>Run</strong> it (UAC prompt will appear — click Yes).</li>
  <li>The <strong>Setup Wizard</strong> appears on first launch — follow the 4 steps.</li>
  <li>You're ready. Click <strong>Tools</strong> to calculate a work report, create a new one, use the Sub-Leaders Panel, or export it.</li>
</ol>

<hr>

<h2>🛠️ Building From Source</h2>

<h3>Prerequisites</h3>
<ul>
  <li>Python <strong>3.10+</strong></li>
  <li>Windows 10 / 11</li>
</ul>

<h3>Install dependencies</h3>
<pre><code>pip install PySide6 Pillow cryptography pyinstaller</code></pre>

<h3>Run the app</h3>
<pre><code>python mta_assistant.py</code></pre>

<h3>Build a standalone .exe</h3>
<pre><code>pyinstaller --onefile --noconsole --uac-admin --icon "logo.ico" --add-data "logo.ico;." --name "MTA Assistant" mta_assistant.py</code></pre>

<p>The finished exe will be in <code>dist/MTA Assistant.exe</code>.</p>

<hr>

<h2>🔑 License System</h2>

<p>MTA Assistant uses a <strong>fully offline</strong> license system based on <strong>Ed25519 signatures</strong>. Every install starts with a <strong>15-day free trial</strong>.</p>

<h3>How it works</h3>
<ol>
  <li>On first launch, the app generates a unique <strong>HWID</strong> (Hardware ID) from your machine's <code>MachineGuid</code>, CPU ID, and motherboard serial number.</li>
  <li>When the trial ends, an <strong>Activation dialog</strong> appears showing your HWID.</li>
  <li>Send your HWID to the seller on Telegram to receive a signed license key.</li>
  <li>Paste the license key — it's verified <strong>locally</strong> without any internet call.</li>
</ol>

<h3>Trial protection</h3>
<ul>
  <li>Clock rollback detection (last seen date + max seen date)</li>
  <li>HWID binding — a license only works on the machine it was issued for</li>
  <li>Tamper flag — once triggered, the trial is permanently disabled</li>
</ul>

<h3>Status display</h3>
<p>The remaining trial or license duration is always visible in the <strong>status bar</strong>, on the <strong>Home page</strong>, and in <strong>Settings</strong>. It refreshes every hour automatically.</p>

<hr>

<h2>🗂️ Folder Structure</h2>
<p>The app expects your MTA:SA folder to contain a <code>screenshots</code> directory with category subfolders:</p>
<pre><code>MTA San Andreas 1.6/
└── screenshots/
    ├── Arrest/
    ├── Kill/
    ├── Shift/
    ├── TakeGun/
    ├── Wanted/
    └── ...</code></pre>
<p>Folder names are matched <strong>case-insensitively</strong> (<code>arrest</code> = <code>ARREST</code> = <code>Arrest</code>). Missing folders are handled gracefully — no errors. You can also auto-create missing folders via <strong>Tools → Create Missing Category Folders</strong>.</p>

<hr>

<h2>💾 Data Storage Locations</h2>

<table>
  <thead><tr><th>Data</th><th>Location</th></tr></thead>
  <tbody>
    <tr><td>MTA folder, faction, rank, name, theme, compression, license, trial info</td><td><code>HKEY_CURRENT_USER\Software\MTA Assistant</code></td></tr>
    <tr><td>Per-faction test questions</td><td><code>%APPDATA%\MTA Assistant\test_questions.json</code></td></tr>
    <tr><td>Work report output</td><td><code>%USERPROFILE%\Desktop\&lt;GameName&gt;\</code> + <code>&lt;GameName&gt;.zip</code></td></tr>
  </tbody>
</table>

<hr>

<h2>💰 Price Lists</h2>

<details>
<summary><b>👮 Police Department</b></summary>
<table>
  <thead><tr><th>Category</th><th>Price</th></tr></thead>
  <tbody>
    <tr><td>Wanted</td><td>$2,000</td></tr>
    <tr><td>Kill</td><td>$1,000</td></tr>
    <tr><td>Arrest</td><td>$6,000</td></tr>
    <tr><td>Shift</td><td>$8,000</td></tr>
    <tr><td>TakeGun</td><td>$3,000</td></tr>
    <tr><td>Ticket</td><td>$10,000</td></tr>
  </tbody>
</table>
</details>

<details>
<summary><b>🚔 Police Federal</b></summary>
<table>
  <thead><tr><th>Category</th><th>Price</th></tr></thead>
  <tbody>
    <tr><td>Arrest</td><td>$5,000</td></tr>
    <tr><td>Kill</td><td>$2,000</td></tr>
    <tr><td>Shift</td><td>$5,000</td></tr>
    <tr><td>TakeGun</td><td>$8,000</td></tr>
    <tr><td>Wanted</td><td>$6,000</td></tr>
  </tbody>
</table>
</details>

<details>
<summary><b>🪖 National Guard</b></summary>
<table>
  <thead><tr><th>Category</th><th>Price</th></tr></thead>
  <tbody>
    <tr><td>Shift</td><td>$7,500</td></tr>
    <tr><td>Arrest</td><td>$2,000</td></tr>
    <tr><td>Wanted</td><td>$2,000</td></tr>
    <tr><td>TakeGun</td><td>$2,000</td></tr>
    <tr><td>Kill</td><td>$4,000</td></tr>
  </tbody>
</table>
</details>

<details>
<summary><b>🚕 Taxi</b> — rank-based</summary>
<table>
  <thead><tr><th>Rank</th><th>Shift</th><th>Service</th></tr></thead>
  <tbody>
    <tr><td>Rank 1</td><td>$7,500</td><td>$6,000</td></tr>
    <tr><td>Rank 2</td><td>$7,500</td><td>$8,500</td></tr>
    <tr><td>Rank 3</td><td>$7,500</td><td>$10,600</td></tr>
    <tr><td>Rank 4</td><td>$7,500</td><td>$13,300</td></tr>
    <tr><td>Rank 5</td><td>$7,500</td><td>$15,000</td></tr>
  </tbody>
</table>
</details>

<details>
<summary><b>🎯 Hitman Agency</b> — rank-based</summary>
<table>
  <thead><tr><th>Rank</th><th>Contract</th></tr></thead>
  <tbody>
    <tr><td>Rank 1</td><td>$15,000</td></tr>
    <tr><td>Rank 2</td><td>$20,000</td></tr>
    <tr><td>Rank 3</td><td>$30,000</td></tr>
    <tr><td>Rank 4</td><td>$35,000</td></tr>
    <tr><td>Rank 5</td><td>$45,000</td></tr>
  </tbody>
</table>
</details>

<details>
<summary><b>🚑 Medic</b> — rank-based</summary>
<table>
  <thead><tr><th>Rank</th><th>Heal</th><th>Service</th></tr></thead>
  <tbody>
    <tr><td>Rank 1</td><td>$6,300</td><td>$5,000</td></tr>
    <tr><td>Rank 2</td><td>$7,000</td><td>$6,000</td></tr>
    <tr><td>Rank 3</td><td>$8,000</td><td>$6,000</td></tr>
    <tr><td>Rank 4</td><td>$9,500</td><td>$7,500</td></tr>
    <tr><td>Rank 5</td><td>$11,000</td><td>$9,000</td></tr>
  </tbody>
</table>
</details>

<details>
<summary><b>📰 New Reporter</b> — rank-based</summary>
<table>
  <thead><tr><th>Rank</th><th>SP</th><th>Day</th><th>Night</th></tr></thead>
  <tbody>
    <tr><td>Rank 1</td><td>$25,000</td><td>$9,000</td><td>$4,000</td></tr>
    <tr><td>Rank 2</td><td>$25,000</td><td>$1,000</td><td>$4,000</td></tr>
    <tr><td>Rank 3</td><td>$25,000</td><td>$12,000</td><td>$5,000</td></tr>
    <tr><td>Rank 4</td><td>$25,000</td><td>$14,000</td><td>$5,000</td></tr>
    <tr><td>Rank 5</td><td>$25,000</td><td>$15,000</td><td>$6,000</td></tr>
  </tbody>
</table>
</details>

<details>
<summary><b>🎓 School Instructor</b> — 🚧 Coming Soon</summary>
<p><strong>Prices for this faction have not been announced yet.</strong></p>
<p>Supported folders:</p>
<ul>
  <li>Mojavez</li>
  <li>Tamdid</li>
  <li>Slot-Gun</li>
  <li>Test</li>
</ul>
</details>

<details>
<summary><b>🔧 Mechanic</b> — 🚧 Coming Soon</summary>
<p><strong>Prices for this faction have not been announced yet.</strong></p>
<p>Supported folders:</p>
<ul>
  <li>Tuning</li>
  <li>towcar</li>
  <li>Repair</li>
  <li>Refill</li>
  <li>Service</li>
</ul>
</details>

<hr>

<h2>🚔 Fine Calculator</h2>

<p>Available only when your current faction is <strong>Police Department</strong>.</p>

<table>
  <thead><tr><th>Location</th><th>Speed Limit</th></tr></thead>
  <tbody>
    <tr><td>LS City</td><td>120 KM/H</td></tr>
    <tr><td>LV City</td><td>170 KM/H</td></tr>
    <tr><td>SF City</td><td>180 KM/H</td></tr>
    <tr><td>Heavy Traffic Areas</td><td>100 KM/H</td></tr>
    <tr><td>Highway / Outside Cities</td><td>240 KM/H</td></tr>
  </tbody>
</table>

<p><strong>Formula:</strong> <code>Total = $5,000 + (⌊(Speed − Limit) / 20⌋ × $2,000)</code></p>

<hr>

<h2>👮 Sub-Leaders Panel — FP Calculator</h2>

<p>Available for <strong>every faction</strong>. The FP Calculator uses the following rules:</p>

<h3>Base FP by Rank</h3>
<table>
  <thead><tr><th>Rank</th><th>Base FP</th></tr></thead>
  <tbody>
    <tr><td>Rank 1</td><td>30</td></tr>
    <tr><td>Rank 2</td><td>20</td></tr>
    <tr><td>Rank 3</td><td>15</td></tr>
    <tr><td>Rank 4</td><td>10</td></tr>
    <tr><td>Rank 5</td><td>5</td></tr>
    <tr><td>Rank 6</td><td>Uses main rank as base</td></tr>
  </tbody>
</table>

<h3>Modifiers</h3>
<ul>
  <li><strong>+15 FP</strong> per FW received</li>
  <li><strong>60 FP</strong> — Resignation in less than 1 week of joining</li>
  <li><strong>80 FP — Direct Kick</strong> — Outlaw / Bad, insulting the leader, high-level insult, 2 FWs in first 7 days, or 4+ total FWs</li>
</ul>

<hr>

<h2>🖥️ Screenshots</h2>
<blockquote><em>Add screenshots of the Home page, Tools, Sub-Leaders Panel, Fine Calculator, and Report table here.</em></blockquote>

<hr>

<h2>📋 Changelog</h2>

<h3>v1.14.0</h3>
<ul>
  <li>👮 <strong>TEST tab</strong> is now available for <strong>every faction</strong> with an editable question list</li>
  <li>📋 <strong>Copy Start Test Message</strong> button restored — shown for <strong>Police Department only</strong></li>
  <li>📝 <strong>Accept / Reject / Log&nbsp;/d</strong> with AV Count restored — shown for <strong>Police Department only</strong></li>
  <li>🔄 PD-only sections now toggle <strong>instantly</strong> when switching faction (no restart needed)</li>
  <li>🎨 Sub-Leaders Panel description adapts to the current faction</li>
  <li>🐛 Fixed PD-only sections not appearing when Police Department was already active at launch</li>
  <li>🐛 Fixed faction switching not updating the visibility of PD-only sections</li>
</ul>

<h3>v1.13.0</h3>
<ul>
  <li>👮 <strong>Sub-Leaders Panel for every faction</strong> — no longer limited to Police Department</li>
  <li>📝 <strong>Fully editable TEST question list</strong> — add, edit, and delete questions per faction. Each question gets its own <strong>Copy / Edit / Delete</strong> row. Saved in <code>%APPDATA%\MTA Assistant\test_questions.json</code></li>
  <li>🌱 Default sample question is now available for every faction that hasn't been customised yet</li>
  <li>🧹 Removed the "Work Report Checker" placeholder tab from the Sub-Leaders Panel</li>
  <li>🎨 Question rows use clean text buttons (Copy / Edit / Delete) instead of icons</li>
</ul>

<h3>v1.12.0</h3>
<ul>
  <li>🔒 <strong>Offline license system</strong> — Ed25519 signature verification, HWID-bound, no internet required</li>
  <li>🕐 <strong>15-day free trial</strong> with clock-rollback and tamper detection</li>
  <li>📊 <strong>License / Trial status display</strong> in the status bar, Home page, and Settings — refreshes hourly</li>
  <li>🔑 <strong>License Activation dialog</strong> with HWID copy button and seller Telegram contact</li>
  <li>🎯 <strong>Faction Stats Dashboard</strong> — visual bar-chart breakdown per category</li>
  <li>🚔 <strong>Fine Calculator</strong> for Police Department (speed violations)</li>
  <li>👮 <strong>Sub-Leaders Panel</strong> for Police Department (TEST + FP Calculator)</li>
</ul>

<h3>v1.11.0</h3>
<ul>
  <li>🎚️ <strong>Compression level</strong> selector remembers your choice</li>
  <li>📈 Progress dialog now shows live <strong>ETA</strong> during conversion</li>
  <li>🧹 Improved error messages and empty-state handling</li>
</ul>

<h3>v1.10.0</h3>
<ul>
  <li>🧙 <strong>First-Time Setup Wizard</strong> — 4 steps with live theme preview and validation</li>
  <li>👁️ <strong>Preview Before Create</strong> — full pre-create dialog with file count, sizes, and target path</li>
  <li>🛡️ <strong>Disk Space Check</strong> — warns before starting if the Desktop drive is nearly full</li>
  <li>🎚️ <strong>Adjustable Compression</strong> — 250 / 200 / 150 KB per image in Settings</li>
  <li>📁 <strong>Create Missing Category Folders</strong> — new tool to auto-create faction folders</li>
</ul>

<h3>v1.9.1</h3>
<ul>
  <li>🔄 <strong>Auto-Update</strong> — silent GitHub release check on launch with clean update dialog</li>
  <li>🎯 Manual update check from <strong>Help → Check for Updates...</strong></li>
  <li>💾 <strong>Skip this version</strong> option stored in the registry</li>
</ul>

<h3>v1.9.0</h3>
<ul>
  <li>📤 <strong>Export reports to CSV &amp; PDF</strong> — directly from the Report page or Tools menu</li>
  <li>🌙 <strong>Dark Mode</strong> — full theme with live toggle, saved in registry</li>
  <li>🖼️ <strong>Screenshot Preview</strong> — double-click a report row to open a gallery of its screenshots</li>
  <li>🎨 Refactored stylesheets into Light and Dark constants</li>
</ul>

<h3>v1.8.0</h3>
<ul>
  <li>🎓 <strong>School Instructor</strong> and 🔧 <strong>Mechanic</strong> added as coming-soon factions with full folder structure</li>
  <li>🔤 Case-insensitive folder matching improved across all factions</li>
  <li>🎯 Factions displayed in a fixed, curated order</li>
  <li>🧹 Removed <code>(rank-based)</code> and <code>(coming soon)</code> labels from the faction picker</li>
  <li>🚫 Clear notification when a coming-soon faction is selected</li>
</ul>

<h3>v1.7.0</h3>
<ul>
  <li>📰 <strong>New Reporter</strong> faction added with rank-based pricing (SP fixed, Day / Night vary)</li>
</ul>

<h3>v1.6.0</h3>
<ul>
  <li>🚕 <strong>Taxi</strong> faction added with rank-based Service pricing (Shift is fixed across all ranks)</li>
</ul>

<h3>v1.5.0</h3>
<ul>
  <li>🎯 <strong>Hitman Agency</strong> faction added (rank-based, single category: Contract)</li>
  <li>🖼️ Custom app icon support via <code>logo.ico</code></li>
</ul>

<h3>v1.4.0</h3>
<ul>
  <li>🚑 <strong>Medic</strong> faction added with <strong>rank-based pricing</strong></li>
  <li>🎚️ New rank selection dialog with live price preview</li>
  <li>🎯 Rank card and menu item shown only for rank-based factions</li>
</ul>

<h3>v1.3.0</h3>
<ul>
  <li>👮 <strong>Police Department</strong> faction added (with optional <code>Ticket</code> category)</li>
</ul>

<h3>v1.2.0</h3>
<ul>
  <li>🚀 Heavy work moved to background thread — <strong>no more freezing</strong></li>
  <li>📈 Live progress dialog with file counter (X / Y files)</li>
  <li>🐛 Fixed: no empty Desktop folder when zero PNGs exist</li>
</ul>

<h3>v1.1.0</h3>
<ul>
  <li>🐛 Fixed: all category folders are now created even if empty</li>
  <li>🔖 Version bump</li>
</ul>

<h3>v1.0.0</h3>
<ul>
  <li>🎉 Initial release</li>
</ul>

<hr>

<h2>🧰 Tech Stack</h2>
<table>
  <thead><tr><th>Layer</th><th>Technology</th></tr></thead>
  <tbody>
    <tr><td>GUI</td><td>PySide6 (Qt 6)</td></tr>
    <tr><td>Image Processing</td><td>Pillow</td></tr>
    <tr><td>License Verification</td><td>cryptography (Ed25519)</td></tr>
    <tr><td>PDF Export</td><td>Qt QPrinter (built-in)</td></tr>
    <tr><td>Auto-Update</td><td>GitHub Releases API (urllib)</td></tr>
    <tr><td>Persistence</td><td>Windows Registry (winreg) + JSON</td></tr>
    <tr><td>Packaging</td><td>PyInstaller</td></tr>
    <tr><td>Language</td><td>Python 3.10+</td></tr>
  </tbody>
</table>

<hr>

<h2>🤝 Contributing</h2>
<p>Found a bug? Want a new faction? Open an issue or submit a pull request — contributions are always welcome.</p>

<hr>

<h2>📄 License</h2>
<p>This project is provided as-is for personal use. See the repository for details.</p>

<hr>

<div align="center">
  <p><strong>Made with ❤️ by AmooReza</strong></p>
  <p>⭐ If you find this useful, consider giving the repo a star!</p>
</div>