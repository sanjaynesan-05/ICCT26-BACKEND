# FRONTEND UPDATE PROMPT - ICCT26 Tournament Registration
Copy and paste this ENTIRE prompt into your VS Code AI assistant to update your frontend:

---

I need to update my frontend to work with my updated ICCT26 backend. Here's what changed and what I need:

## BACKEND CHANGES SUMMARY

### 1. REGISTRATION FLOW CHANGED
**OLD BEHAVIOR:**
- Registration returned team_id immediately
- Files uploaded directly to permanent storage

**NEW BEHAVIOR:**
- Registration returns "pending" status (NO team_id shown to user)
- Files uploaded to Cloudinary /pending/ folder
- User must wait for admin confirmation
- Team ID is only revealed AFTER admin approves via email

### 2. CLOUD-FIRST FILE STORAGE
All files now stored in Cloudinary with organized folder structure:
- **Pending files:** `/icct26-tournament/pending/{team_id}/`
- **Confirmed files:** `/icct26-tournament/confirmed/{team_id}/` (with Team ID in filename)
- **Rejected files:** Deleted immediately from Cloudinary

### 3. ADMIN WORKFLOW
- Admin reviews pending teams
- On APPROVE: Files move to /confirmed/ with Team ID in filename, email sent
- On REJECT: Files deleted from Cloudinary, cost = $0

---

## API ENDPOINTS DOCUMENTATION

### BASE URL
```
Development: http://localhost:8000
Production: https://your-backend-url.com
```

### 1. TEAM REGISTRATION
```http
POST /register/team
Content-Type: multipart/form-data
```

**Form Fields:**
```javascript
{
  // Team Info
  team_name: string (required),
  church_name: string (required),
  
  // Captain Info
  captain_name: string (required),
  captain_phone: string (required, 10 digits),
  captain_email: string (required),
  captain_whatsapp: string (required),
  
  // Vice Captain Info
  vice_name: string (required),
  vice_phone: string (required),
  vice_email: string (required),
  vice_whatsapp: string (required),
  
  // Files (multipart)
  pastor_letter: File (required, PDF/Image, max 5MB),
  payment_receipt: File (optional, PDF/Image, max 5MB),
  group_photo: File (optional, Image, max 5MB),
  
  // Players (dynamic array)
  player_0_name: string,
  player_0_role: string (Batsman/Bowler/All-Rounder/Wicket-Keeper),
  player_0_aadhar_file: File (optional),
  player_0_subscription_file: File (optional),
  
  player_1_name: string,
  player_1_role: string,
  // ... continue for all players
}
```

**SUCCESS Response (200):**
```json
{
  "success": true,
  "message": "Registration submitted successfully. Please wait for admin confirmation.",
  "team_name": "Grace Church Warriors",
  "player_count": 15,
  "registration_status": "pending",
  "files_uploaded": ["pastor_letter", "payment_receipt", "group_photo"],
  "storage_location": "cloudinary_pending"
}
```

**KEY CHANGES:**
- ❌ NO `team_id` in response (hidden until approval)
- ✅ Show "pending" status
- ✅ Show confirmation message to wait for email
- ✅ Files uploaded to Cloudinary pending folder

**VALIDATION ERRORS (400):**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Validation failed",
  "field": "captain_email",
  "details": "Invalid email format"
}
```

### 2. ADMIN - GET ALL TEAMS
```http
GET /admin/teams?status=pending
```

**Query Parameters:**
- `status` (optional): Filter by "pending" | "confirmed" | "rejected"

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "teamId": "ICCT26-abc123",
      "teamName": "Grace Church Warriors",
      "churchName": "Grace Community Church",
      "captain": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "9876543210"
      },
      "viceCaptain": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "9876543211"
      },
      "playerCount": 15,
      "registrationDate": "2025-12-21T10:30:00Z",
      "registrationStatus": "pending",
      "paymentReceipt": "https://res.cloudinary.com/.../pending/ICCT26-abc123/payment_receipt",
      "pastorLetter": "https://res.cloudinary.com/.../pending/ICCT26-abc123/pastor_letter",
      "groupPhoto": "https://res.cloudinary.com/.../pending/ICCT26-abc123/group_photo"
    }
  ]
}
```

### 3. ADMIN - GET TEAM DETAILS
```http
GET /admin/teams/{team_id}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "team": {
      "teamId": "ICCT26-abc123",
      "teamName": "Grace Church Warriors",
      "churchName": "Grace Community Church",
      "captain": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "9876543210",
        "whatsapp": "9876543210"
      },
      "viceCaptain": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "phone": "9876543211",
        "whatsapp": "9876543211"
      },
      "registrationStatus": "pending",
      "registrationDate": "2025-12-21T10:30:00Z",
      "paymentReceipt": "https://res.cloudinary.com/.../payment_receipt",
      "pastorLetter": "https://res.cloudinary.com/.../pastor_letter",
      "groupPhoto": "https://res.cloudinary.com/.../group_photo"
    },
    "players": [
      {
        "playerId": "ICCT26-abc123-P01",
        "name": "Player One",
        "role": "Batsman",
        "aadharFile": "https://res.cloudinary.com/.../aadhar",
        "subscriptionFile": "https://res.cloudinary.com/.../subscription"
      }
      // ... more players
    ]
  }
}
```

### 4. ADMIN - CONFIRM/APPROVE TEAM
```http
PUT /admin/teams/{team_id}/confirm
```

**Response:**
```json
{
  "success": true,
  "message": "Team registration confirmed successfully",
  "team_id": "ICCT26-abc123",
  "registration_status": "confirmed",
  "email_notification": "sent",
  "files_confirmed": ["payment_receipt", "pastor_letter", "group_photo"],
  "storage_info": {
    "old_location": "cloudinary: /pending/ICCT26-abc123/",
    "new_location": "cloudinary: /confirmed/ICCT26-abc123/ (with Team ID in filenames)",
    "example": "ICCT26-abc123_payment_receipt.pdf, ICCT26-abc123_pastor_letter.pdf"
  }
}
```

**What happens:**
1. Files move from `/pending/` to `/confirmed/`
2. Files renamed with Team ID (e.g., `ICCT26-abc123_payment_receipt.pdf`)
3. Database updated with new URLs
4. Email sent to captain with Team ID
5. Status changed to "confirmed"

### 5. ADMIN - REJECT TEAM
```http
PUT /admin/teams/{team_id}/reject
```

**Response:**
```json
{
  "success": true,
  "message": "Team registration rejected",
  "team_id": "ICCT26-abc123",
  "registration_status": "rejected",
  "files_deleted": true,
  "deletion_status": "instant",
  "cost_impact": "$0 (files deleted from Cloudinary)"
}
```

**What happens:**
1. All files deleted from Cloudinary `/pending/{team_id}/`
2. Database updated: status = "rejected", URLs cleared
3. Cost: $0 (deleted files don't count)

### 6. HEALTH CHECK
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ICCT26 Registration API",
  "timestamp": "2025-12-21T10:30:00Z",
  "version": "1.0.0"
}
```

### 7. SYSTEM STATUS
```http
GET /status
```

**Response:**
```json
{
  "status": "operational",
  "database": "connected",
  "cloudinary": "configured",
  "smtp_enabled": true,
  "timestamp": "2025-12-21T10:30:00Z"
}
```

---

## FRONTEND REQUIREMENTS

### 1. REGISTRATION PAGE UPDATES

**BEFORE SUBMISSION:**
```jsx
// Show normal registration form
<form onSubmit={handleSubmit}>
  <input name="team_name" required />
  <input name="captain_email" required />
  <input type="file" name="pastor_letter" required />
  {/* ... all fields */}
  <button type="submit">Register Team</button>
</form>
```

**AFTER SUCCESSFUL SUBMISSION:**
```jsx
// NEW: Show pending status message (NO team_id)
<div className="success-message">
  <h2>✅ Registration Submitted!</h2>
  <p>Your team "{teamName}" has been registered.</p>
  <p>Status: <strong>Pending Admin Approval</strong></p>
  <p>You will receive a confirmation email with your Team ID once approved.</p>
  <p>Please check your email: {captainEmail}</p>
</div>
```

**KEY CHANGES:**
- ❌ Don't show Team ID (not available yet)
- ✅ Show "Pending" status
- ✅ Tell user to wait for email
- ✅ Show captain email where confirmation will be sent

### 2. ADMIN PANEL UPDATES

**Admin Dashboard Layout:**
```jsx
// Three tabs: Pending, Confirmed, Rejected
<Tabs>
  <Tab label="Pending" count={pendingCount}>
    <TeamList status="pending" />
  </Tab>
  <Tab label="Confirmed" count={confirmedCount}>
    <TeamList status="confirmed" />
  </Tab>
  <Tab label="Rejected" count={rejectedCount}>
    <TeamList status="rejected" />
  </Tab>
</Tabs>
```

**Team Review Component:**
```jsx
function TeamReviewCard({ team }) {
  const [loading, setLoading] = useState(false);
  
  const handleApprove = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/admin/teams/${team.teamId}/confirm`, {
        method: 'PUT'
      });
      const data = await response.json();
      
      if (data.success) {
        alert(`✅ Team approved! Email ${data.email_notification}`);
        // Refresh team list
      }
    } catch (error) {
      alert('❌ Error approving team');
    }
    setLoading(false);
  };
  
  const handleReject = async () => {
    if (!confirm('Are you sure? Files will be deleted permanently!')) return;
    
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/admin/teams/${team.teamId}/reject`, {
        method: 'PUT'
      });
      const data = await response.json();
      
      if (data.success) {
        alert('❌ Team rejected. Files deleted from Cloudinary.');
        // Refresh team list
      }
    } catch (error) {
      alert('❌ Error rejecting team');
    }
    setLoading(false);
  };
  
  return (
    <div className="team-card">
      <h3>{team.teamName}</h3>
      <p>Church: {team.churchName}</p>
      <p>Captain: {team.captain.name} ({team.captain.email})</p>
      <p>Players: {team.playerCount}</p>
      <p>Status: <span className={`status-${team.registrationStatus}`}>
        {team.registrationStatus}
      </span></p>
      
      {/* File Preview */}
      <div className="files">
        {team.paymentReceipt && (
          <a href={team.paymentReceipt} target="_blank">
            📄 Payment Receipt
          </a>
        )}
        {team.pastorLetter && (
          <a href={team.pastorLetter} target="_blank">
            📄 Pastor Letter
          </a>
        )}
        {team.groupPhoto && (
          <a href={team.groupPhoto} target="_blank">
            🖼️ Group Photo
          </a>
        )}
      </div>
      
      {/* Actions (only for pending) */}
      {team.registrationStatus === 'pending' && (
        <div className="actions">
          <button 
            onClick={handleApprove} 
            disabled={loading}
            className="approve-btn"
          >
            ✅ Approve
          </button>
          <button 
            onClick={handleReject} 
            disabled={loading}
            className="reject-btn"
          >
            ❌ Reject
          </button>
        </div>
      )}
    </div>
  );
}
```

### 3. FILE PREVIEW COMPONENT

**Direct Cloudinary URLs (No server-side file serving needed):**
```jsx
function FilePreview({ url, type }) {
  if (!url) return null;
  
  return (
    <div className="file-preview">
      {type === 'image' ? (
        <img src={url} alt="Preview" style={{maxWidth: '200px'}} />
      ) : (
        <a href={url} target="_blank" rel="noopener noreferrer">
          📄 View File
        </a>
      )}
      <a href={url} download>
        ⬇️ Download
      </a>
    </div>
  );
}
```

---

## EXAMPLE API CALLS

### JavaScript/Fetch
```javascript
// Registration
async function registerTeam(formData) {
  try {
    const response = await fetch('http://localhost:8000/register/team', {
      method: 'POST',
      body: formData // FormData object with all fields
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Show success message
      console.log('Registration Status:', data.registration_status); // "pending"
      console.log('Message:', data.message);
      // NO team_id available!
    } else {
      // Show error
      console.error('Error:', data.message);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
}

// Admin: Get pending teams
async function getPendingTeams() {
  const response = await fetch('http://localhost:8000/admin/teams?status=pending');
  const data = await response.json();
  return data.data; // Array of teams
}

// Admin: Approve team
async function approveTeam(teamId) {
  const response = await fetch(`http://localhost:8000/admin/teams/${teamId}/confirm`, {
    method: 'PUT'
  });
  const data = await response.json();
  
  console.log('Email status:', data.email_notification); // "sent"
  console.log('Files moved to:', data.storage_info.new_location);
  return data;
}

// Admin: Reject team
async function rejectTeam(teamId) {
  const response = await fetch(`http://localhost:8000/admin/teams/${teamId}/reject`, {
    method: 'PUT'
  });
  const data = await response.json();
  
  console.log('Files deleted:', data.files_deleted); // true
  console.log('Cost impact:', data.cost_impact); // "$0"
  return data;
}
```

### Axios
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Registration
const registerTeam = async (formData) => {
  const { data } = await api.post('/register/team', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return data;
};

// Admin endpoints
const adminAPI = {
  getTeams: (status) => api.get(`/admin/teams?status=${status}`),
  approveTeam: (teamId) => api.put(`/admin/teams/${teamId}/confirm`),
  rejectTeam: (teamId) => api.put(`/admin/teams/${teamId}/reject`)
};
```

---

## CRITICAL FRONTEND CHANGES NEEDED

### ✅ MUST DO:
1. **Remove Team ID display** from registration success page
2. **Show "Pending" status** after registration
3. **Add message**: "Wait for email confirmation with Team ID"
4. **Update Admin Panel** with Pending/Confirmed/Rejected tabs
5. **Add Approve/Reject buttons** for pending teams
6. **File previews** using direct Cloudinary URLs
7. **Update API base URL** for production

### ⚠️ DON'T DO:
1. ❌ Don't show team_id in registration response (not available)
2. ❌ Don't create local file serving endpoints (files are in Cloudinary)
3. ❌ Don't assume registration means automatic approval
4. ❌ Don't skip the "pending" status message

---

## TESTING CHECKLIST

- [ ] Registration returns "pending" status (NO team_id)
- [ ] Success message tells user to wait for email
- [ ] Admin can see pending teams
- [ ] Admin can view files (Cloudinary URLs work)
- [ ] Approve button works, email sent
- [ ] Reject button works, files deleted
- [ ] Confirmed teams show in "Confirmed" tab
- [ ] Rejected teams show in "Rejected" tab
- [ ] File previews work (direct Cloudinary links)

---

## PRODUCTION DEPLOYMENT

When deploying frontend:
1. Update `API_BASE` to production URL
2. Test end-to-end flow
3. Verify email delivery
4. Check Cloudinary file uploads
5. Test admin approval/rejection

---

Please update my frontend code to implement these changes. Focus on:
1. Registration success page (show pending, no team_id)
2. Admin panel with tabs (Pending/Confirmed/Rejected)
3. Team review cards with Approve/Reject buttons
4. File preview using Cloudinary URLs
5. API integration using the endpoints above

Thank you!
