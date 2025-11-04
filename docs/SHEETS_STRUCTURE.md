# 📊 Google Sheets Structure - One Sheet Per Team

## Overview

Each team registration creates **TWO things**:

1. **One dedicated worksheet** for the team with ALL their details
2. **One entry in Teams_Index** worksheet for quick overview

---

## 📁 Google Sheets File Structure

```
📗 ICCT26 Tournament Registration (Main Spreadsheet)
│
├── 📄 Teams_Index (Master list of all teams)
├── 📄 ICCT26-0001_Warriors (Team 1's complete data)
├── 📄 ICCT26-0002_Crusaders (Team 2's complete data)
├── 📄 ICCT26-0003_Champions (Team 3's complete data)
└── ... (more team sheets)
```

---

## 📄 Teams_Index Sheet (Master Overview)

This sheet contains a summary of all registered teams:

| Team ID | Team Name | Church Name | Captain Name | Vice-Captain | Players | Status | Registration Date | Sheet Link |
|---------|-----------|-------------|--------------|--------------|---------|--------|-------------------|------------|
| ICCT26-0001 | Warriors | St. Mary's Church | John Doe | Jane Smith | 11 | Registered | 2025-11-04 10:30:00 | [Link to Warriors Sheet] |
| ICCT26-0002 | Crusaders | Holy Cross Church | Mike Wilson | Sarah Lee | 13 | Registered | 2025-11-04 11:15:00 | [Link to Crusaders Sheet] |
| ICCT26-0003 | Champions | Grace Church | David Brown | Emma Davis | 15 | Registered | 2025-11-04 12:00:00 | [Link to Champions Sheet] |

**Use this sheet for:**
- Quick overview of all teams
- Easy navigation to individual team sheets
- Summary statistics

---

## 📄 Individual Team Sheet (Example: ICCT26-0001_Warriors)

Each team gets their own dedicated worksheet with complete details:

```
┌────────────────────────────────────────────────────────────────┐
│  TEAM REGISTRATION: ICCT26-0001                                │
└────────────────────────────────────────────────────────────────┘

  TEAM INFORMATION
  ─────────────────────────────────────────
  Team ID:              ICCT26-0001
  Team Name:            Warriors
  Church Name:          St. Mary's Church
  Registration Date:    2025-11-04 10:30:00
  Status:               Registered
  Total Players:        11

  CAPTAIN DETAILS
  ─────────────────────────────────────────
  Name:                 John Doe
  Phone:                +91 9876543210
  WhatsApp:             9876543210
  Email:                john.doe@email.com

  VICE-CAPTAIN DETAILS
  ─────────────────────────────────────────
  Name:                 Jane Smith
  Phone:                +91 9876543211
  WhatsApp:             9876543211
  Email:                jane.smith@email.com

  UPLOADED FILES
  ─────────────────────────────────────────
  Pastor Letter:        https://drive.google.com/file/d/xxxxx/view
  Payment Receipt:      https://drive.google.com/file/d/yyyyy/view

  PLAYERS LIST
  ─────────────────────────────────────────────────────────────────────────────────────────
  #  | Name           | Age | Phone          | Role         | Aadhar Link              | Subscription Link
  ───┼────────────────┼─────┼────────────────┼──────────────┼──────────────────────────┼─────────────────────
  1  | Player One     | 25  | 9876543212     | Batsman      | [Google Drive Link]      | [Google Drive Link]
  2  | Player Two     | 28  | 9876543213     | Bowler       | [Google Drive Link]      | [Google Drive Link]
  3  | Player Three   | 22  | 9876543214     | All-Rounder  | [Google Drive Link]      | [Google Drive Link]
  4  | Player Four    | 30  | 9876543215     | Wicket Keeper| [Google Drive Link]      | [Google Drive Link]
  5  | Player Five    | 26  | 9876543216     | Batsman      | [Google Drive Link]      | [Google Drive Link]
  6  | Player Six     | 24  | 9876543217     | Bowler       | [Google Drive Link]      | [Google Drive Link]
  7  | Player Seven   | 27  | 9876543218     | All-Rounder  | [Google Drive Link]      | [Google Drive Link]
  8  | Player Eight   | 29  | 9876543219     | Batsman      | [Google Drive Link]      | [Google Drive Link]
  9  | Player Nine    | 23  | 9876543220     | Bowler       | [Google Drive Link]      | [Google Drive Link]
  10 | Player Ten     | 31  | 9876543221     | All-Rounder  | [Google Drive Link]      | [Google Drive Link]
  11 | Player Eleven  | 25  | 9876543222     | Batsman      | [Google Drive Link]      | [Google Drive Link]
```

---

## ✨ Benefits of This Approach

### 1. **Easy to View Complete Team Data**
- All team information in one place
- No need to cross-reference multiple sheets
- Direct links to all uploaded files

### 2. **Better Organization**
- Each team has dedicated space
- Sheet tabs clearly labeled with Team ID and name
- Easy to navigate between teams

### 3. **Convenient File Access**
- Clickable links to Google Drive files
- Aadhar and Subscription cards linked to each player
- Pastor letter and payment receipt at top

### 4. **Professional Appearance**
- Formatted sections with headers
- Color-coded headers
- Auto-sized columns for readability

### 5. **Quick Overview with Teams_Index**
- See all teams at a glance
- Sort and filter easily
- Jump to any team sheet with one click

---

## 🎯 Use Cases

### For Tournament Organizers
1. **Team Review:** Click on any team's sheet link from Teams_Index
2. **Document Verification:** Click file links to verify documents
3. **Contact Players:** All phone numbers and emails in one place
4. **Player Statistics:** See age, roles at a glance

### For Data Analysis
1. **Export Individual Teams:** Each team sheet can be exported separately
2. **Share with Others:** Share specific team sheet without exposing all teams
3. **Print Registration:** Print team sheet for offline record

### For Registration Desk
1. **Quick Lookup:** Find team by ID or name in Teams_Index
2. **Verify Documents:** Check all file links are present
3. **Contact Captain:** Get captain's contact info immediately

---

## 📋 What Gets Stored in Each Team Sheet

### Team Information Section
- Team ID (e.g., ICCT26-0001)
- Team Name
- Church Name
- Registration Date & Time
- Status (Registered/Pending/etc.)
- Total Player Count

### Captain & Vice-Captain Details
- Full Name
- Phone Number
- WhatsApp Number
- Email Address

### Uploaded Files
- Pastor Letter (Google Drive link)
- Payment Receipt (Google Drive link)

### Players List (Table Format)
For each player:
- Serial Number (1-15)
- Player Name
- Age
- Phone Number
- Role (Batsman/Bowler/All-Rounder/Wicket Keeper)
- Aadhar Card (Google Drive link)
- Subscription Card (Google Drive link)

---

## 🔄 How It Works

### When Team Registers:

1. **Step 1:** Files uploaded to Google Drive (organized in team folder)
2. **Step 2:** New worksheet created with Team ID + Team Name
3. **Step 3:** All team data formatted and saved to the worksheet
4. **Step 4:** File links from Drive added to the worksheet
5. **Step 5:** Summary added to Teams_Index with link to team sheet

### Result:
- ✅ One complete team sheet with ALL information
- ✅ One row in Teams_Index for quick access
- ✅ All files organized in Google Drive
- ✅ All links working and clickable

---

## 🎨 Visual Formatting

### Sheet Formatting Features:
- **Bold Headers:** All section titles in bold
- **Merged Cells:** Title spans multiple columns
- **Color-Coded:** Headers have gray background
- **Auto-Resize:** Columns automatically sized
- **Hyperlinks:** All Drive links are clickable

### Navigation:
- **Sheet Tabs:** Bottom of screen shows all team sheets
- **Teams_Index:** First sheet for quick navigation
- **Direct Links:** Click sheet link in Teams_Index to jump to team

---

## 📊 Sample Data Flow

```
Frontend Form
    ↓
Registration API
    ↓
┌─────────────────────────────────┐
│  Save to Google Drive           │
│  - Create team folder           │
│  - Upload all files             │
│  - Get file links               │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Create Team Worksheet          │
│  - Team ID + Team Name          │
│  - Format sections              │
│  - Add team data                │
│  - Add file links               │
│  - Add player table             │
└─────────────────────────────────┘
    ↓
┌─────────────────────────────────┐
│  Update Teams_Index             │
│  - Add summary row              │
│  - Add link to team sheet       │
└─────────────────────────────────┘
    ↓
Success Response
```

---

## 🎉 Result

**Before:** Scattered data in multiple sheets, files in Drive folders

**After:** 
- ✅ Each team has complete data in ONE dedicated sheet
- ✅ Easy to view, share, and manage
- ✅ All files linked and accessible
- ✅ Professional, organized, easy to navigate

**Perfect for:** Tournament management, document verification, team lookup, and data export!

---

**Last Updated:** November 4, 2025
