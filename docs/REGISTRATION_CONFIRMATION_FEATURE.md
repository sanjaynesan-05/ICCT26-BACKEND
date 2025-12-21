# Registration Confirmation Feature

## Overview
This feature implements a two-step registration process where team registrations require admin approval before being confirmed.

## How It Works

### 1. Team Registration Flow
When a team submits their registration:
- ✅ Registration is saved to database with `registration_status = 'pending'`
- ✅ Team receives a confirmation message: **"Registration submitted successfully. Please wait for admin confirmation."**
- ❌ **Team ID is NOT shown** to the user (hidden for security)
- ✅ Team appears in admin panel under "pending" registrations

### 2. Admin Confirmation Flow
Admin can review and take action on pending registrations:
- **View pending teams**: Filter teams by status in admin panel
- **Confirm registration**: Approve the team (status → `confirmed`)
- **Reject registration**: Reject the team (status → `rejected`)

### 3. Registration Statuses
- **`pending`**: Initial status after registration (awaiting admin review)
- **`confirmed`**: Approved by admin (team can participate)
- **`rejected`**: Rejected by admin (team cannot participate)

---

## Database Changes

### New Column Added to `teams` Table
```sql
ALTER TABLE teams 
ADD COLUMN registration_status VARCHAR(20) 
NOT NULL DEFAULT 'pending';

CREATE INDEX idx_registration_status ON teams(registration_status);
```

### Migration Script
Run the migration to add the new column:
```bash
python scripts/add_registration_status.py
```

**Note**: Existing teams will be automatically set to `confirmed` status.

---

## API Endpoints

### 1. Team Registration (Updated)
**Endpoint**: `POST /api/register/team`

**Response** (Updated - No Team ID):
```json
{
  "success": true,
  "team_name": "Eagles Cricket Team",
  "message": "Registration submitted successfully. Please wait for admin confirmation.",
  "player_count": 15,
  "registration_status": "pending"
}
```

**Previous Response** (Old - Showed Team ID):
```json
{
  "success": true,
  "team_id": "TEAM-20251221-ABC123",  // ❌ No longer shown
  "team_name": "Eagles Cricket Team",
  "message": "Team registered successfully",
  "player_count": 15
}
```

---

### 2. Get All Teams (Updated - With Filter)
**Endpoint**: `GET /api/admin/teams?status=pending`

**Query Parameters**:
- `status` (optional): Filter by registration status
  - `pending` - Teams waiting for confirmation
  - `confirmed` - Approved teams
  - `rejected` - Rejected teams
  - If not provided, returns all teams

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "teamId": "TEAM-20251221-ABC123",
      "teamName": "Eagles Cricket Team",
      "churchName": "St. Mary's Church",
      "captainName": "John Doe",
      "captainPhone": "+91 9876543210",
      "captainEmail": "john@example.com",
      "viceCaptainName": "Jane Smith",
      "viceCaptainPhone": "+91 9876543211",
      "viceCaptainEmail": "jane@example.com",
      "playerCount": 15,
      "registrationDate": "2025-12-21 10:30:00",
      "registrationStatus": "pending",  // ✅ NEW FIELD
      "paymentReceipt": "https://res.cloudinary.com/...",
      "pastorLetter": "https://res.cloudinary.com/...",
      "groupPhoto": "https://res.cloudinary.com/..."
    }
  ]
}
```

---

### 3. Confirm Team Registration (NEW)
**Endpoint**: `PUT /api/admin/teams/{team_id}/confirm`

**Description**: Approve a pending team registration

**Response**:
```json
{
  "success": true,
  "message": "Team registration confirmed successfully",
  "team_id": "TEAM-20251221-ABC123",
  "registration_status": "confirmed"
}
```

---

### 4. Reject Team Registration (NEW)
**Endpoint**: `PUT /api/admin/teams/{team_id}/reject`

**Description**: Reject a pending team registration

**Response**:
```json
{
  "success": true,
  "message": "Team registration rejected",
  "team_id": "TEAM-20251221-ABC123",
  "registration_status": "rejected"
}
```

---

### 5. Get Team Details (Updated)
**Endpoint**: `GET /api/admin/teams/{team_id}`

**Response** (includes registration status):
```json
{
  "success": true,
  "data": {
    "team": {
      "teamId": "TEAM-20251221-ABC123",
      "teamName": "Eagles Cricket Team",
      "churchName": "St. Mary's Church",
      "registrationStatus": "pending",  // ✅ NEW FIELD
      "captain": { ... },
      "viceCaptain": { ... },
      ...
    },
    "players": [ ... ]
  }
}
```

---

## Frontend Integration Guide

### 1. Registration Page Updates
After successful registration, show:
```javascript
// ❌ OLD: Showed team ID
alert(`Registration successful! Your Team ID is: ${response.team_id}`);

// ✅ NEW: Hide team ID, show confirmation message
if (response.success && response.registration_status === 'pending') {
  alert('Registration submitted successfully! Please wait for admin confirmation.');
  // Or show a nice confirmation modal
}
```

### 2. Admin Panel - Pending Registrations Section
Create tabs/sections to filter teams:

```javascript
// Fetch pending teams
const pendingTeams = await fetch('/api/admin/teams?status=pending');

// Fetch confirmed teams
const confirmedTeams = await fetch('/api/admin/teams?status=confirmed');

// Fetch rejected teams
const rejectedTeams = await fetch('/api/admin/teams?status=rejected');
```

### 3. Admin Panel - Action Buttons
For each pending team, show confirm/reject buttons:

```javascript
// Confirm team
async function confirmTeam(teamId) {
  const response = await fetch(`/api/admin/teams/${teamId}/confirm`, {
    method: 'PUT'
  });
  
  if (response.ok) {
    alert('Team confirmed successfully!');
    // Refresh the list
    loadPendingTeams();
  }
}

// Reject team
async function rejectTeam(teamId) {
  const response = await fetch(`/api/admin/teams/${teamId}/reject`, {
    method: 'PUT'
  });
  
  if (response.ok) {
    alert('Team rejected');
    // Refresh the list
    loadPendingTeams();
  }
}
```

### 4. Display Registration Status
Show status badges in admin panel:

```javascript
function getStatusBadge(status) {
  const badges = {
    pending: '<span class="badge badge-warning">⏳ Pending</span>',
    confirmed: '<span class="badge badge-success">✅ Confirmed</span>',
    rejected: '<span class="badge badge-danger">❌ Rejected</span>'
  };
  return badges[status] || badges.pending;
}
```

---

## Admin Workflow Example

### Step-by-Step Process:

1. **Team Registers**
   - Team submits registration form
   - Backend creates team with `status = 'pending'`
   - Team sees: "Registration submitted. Wait for confirmation."

2. **Admin Reviews**
   - Admin opens admin panel
   - Navigates to "Pending Registrations" tab
   - Sees list of teams with `status = 'pending'`
   - Reviews team details, payment receipt, pastor letter, player list

3. **Admin Takes Action**
   - **Option A: Confirm** → Click "Confirm" button → Team status becomes `confirmed`
   - **Option B: Reject** → Click "Reject" button → Team status becomes `rejected`

4. **Post-Confirmation**
   - Confirmed teams appear in "Confirmed Teams" section
   - Only confirmed teams can participate in matches
   - Team ID can now be shared with confirmed teams (optional)

---

## Testing Steps

### 1. Run Database Migration
```bash
cd "d:\ICCT26 BACKEND"
python scripts/add_registration_status.py
```

Expected output:
```
✅ Successfully added 'registration_status' column
✅ Created index 'idx_registration_status'
✅ Updated X existing teams to 'confirmed' status
```

### 2. Test Registration Flow
```bash
# Register a new team
POST /api/register/team
# Verify response doesn't include team_id
# Verify registration_status = 'pending'
```

### 3. Test Admin Endpoints
```bash
# Get pending teams
GET /api/admin/teams?status=pending

# Confirm a team
PUT /api/admin/teams/TEAM-20251221-ABC123/confirm

# Reject a team
PUT /api/admin/teams/TEAM-20251221-ABC123/reject

# Get confirmed teams
GET /api/admin/teams?status=confirmed
```

---

## Security Benefits

1. **Team ID Hidden**: Prevents unauthorized access using team IDs
2. **Manual Review**: Admin can verify all documents before approval
3. **Quality Control**: Ensures all registrations meet tournament requirements
4. **Fraud Prevention**: Reduces fake/spam registrations

---

## Backend Files Modified

1. ✅ `models.py` - Added `registration_status` column
2. ✅ `scripts/add_registration_status.py` - Migration script
3. ✅ `app/routes/registration_production.py` - Updated response (hide team_id)
4. ✅ `app/routes/admin.py` - Added confirm/reject endpoints + status filter
5. ✅ `app/services.py` - Added `update_team_registration_status()` method

---

## Next Steps for Frontend

1. **Registration Success Page**: Update to show "Wait for confirmation" message
2. **Admin Panel Tabs**: Create separate sections for:
   - Pending Registrations (⏳)
   - Confirmed Teams (✅)
   - Rejected Teams (❌)
3. **Action Buttons**: Add confirm/reject buttons for each pending team
4. **Status Badges**: Display visual indicators for registration status
5. **Email Notifications** (Optional): Notify teams when confirmed/rejected

---

## Questions or Issues?

If you encounter any problems:
1. Check database migration ran successfully
2. Verify API endpoints return `registration_status` field
3. Check logs for any errors
4. Test with Postman/Thunder Client first before frontend integration

All set! 🚀
