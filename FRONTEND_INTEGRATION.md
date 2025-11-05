# 🔗 Frontend Integration Guide

Complete guide to connect your frontend registration page with the ICCT26 backend API.

---

## ✅ Backend Status - Ready for Frontend

Your backend is **100% ready** to receive data from a frontend registration page! 

### What the Backend Accepts
- ✅ Team registration with 11-15 players
- ✅ Captain and Vice-Captain details
- ✅ Base64 encoded PDF files (Aadhar, Subscription, Pastor Letter, Payment Receipt)
- ✅ Player details with roles (Batsman, Bowler, All-Rounder, Wicket Keeper)
- ✅ Automatic email confirmation to captain
- ✅ Database persistence
- ✅ CORS support for cross-origin requests

---

## 🚀 Quick Start - 5 Minutes

### 1. Ensure Backend is Running

```bash
cd "d:\ICCT26 BACKEND"
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**You should see:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Test API Availability

Open browser: **http://localhost:8000/docs**

You will see:
- ✅ Swagger interactive API documentation
- ✅ `/register/team` endpoint ready
- ✅ Request/response examples
- ✅ Try it out button for testing

---

## 📡 API Endpoint Details

### Endpoint URL
```
POST http://localhost:8000/register/team
```

### Content-Type
```
application/json
```

### Request Body Structure

```json
{
  "churchName": "string",
  "teamName": "string",
  "pastorLetter": "base64-pdf-string or null",
  "captain": {
    "name": "string",
    "phone": "string (10-15 digits)",
    "whatsapp": "string (10 digits)",
    "email": "valid-email@example.com"
  },
  "viceCaptain": {
    "name": "string",
    "phone": "string (10-15 digits)",
    "whatsapp": "string (10 digits)",
    "email": "valid-email@example.com"
  },
  "players": [
    {
      "name": "string",
      "age": "integer (15-60)",
      "phone": "string (10-15 digits)",
      "role": "Batsman | Bowler | All-Rounder | Wicket Keeper",
      "aadharFile": "base64-pdf-string or null",
      "subscriptionFile": "base64-pdf-string or null"
    }
  ],
  "paymentReceipt": "base64-pdf-string or null"
}
```

### Validation Rules

| Field | Rules |
|-------|-------|
| `churchName` | Required, 1-200 characters |
| `teamName` | Required, 1-100 characters |
| `captain.email` | Valid email address |
| `captain.phone` | 10-15 digits, optional |
| `viceCaptain.phone` | 10-15 digits, optional |
| `players` | Minimum 11, Maximum 15 players |
| `players[].age` | 15-60 years old |
| `players[].role` | One of: Batsman, Bowler, All-Rounder, Wicket Keeper |
| PDF files | Optional, base64 encoded strings |

---

## 💻 Frontend Implementation Examples

### 1. HTML + Vanilla JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <title>ICCT26 Team Registration</title>
    <style>
        body { font-family: Arial; max-width: 1000px; margin: 50px auto; }
        form { background: #f5f5f5; padding: 20px; border-radius: 8px; }
        label { display: block; margin: 10px 0 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }
        .player-section { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .btn { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .message { margin-top: 20px; padding: 10px; border-radius: 4px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>🏏 ICCT26 Cricket Tournament - Team Registration</h1>

    <form id="registrationForm">
        <!-- Church and Team Info -->
        <h2>Team Information</h2>
        <label>Church Name:</label>
        <input type="text" id="churchName" required>

        <label>Team Name:</label>
        <input type="text" id="teamName" required>

        <label>Pastor Letter (PDF):</label>
        <input type="file" id="pastorLetterFile" accept=".pdf">

        <!-- Captain Details -->
        <h2>Captain Details</h2>
        <label>Captain Name:</label>
        <input type="text" id="captainName" required>

        <label>Captain Email:</label>
        <input type="email" id="captainEmail" required>

        <label>Captain Phone:</label>
        <input type="tel" id="captainPhone" placeholder="+91 or 10 digits">

        <label>Captain WhatsApp (10 digits):</label>
        <input type="text" id="captainWhatsapp" maxlength="10">

        <!-- Vice-Captain Details -->
        <h2>Vice-Captain Details</h2>
        <label>Vice-Captain Name:</label>
        <input type="text" id="viceCaptainName" required>

        <label>Vice-Captain Email:</label>
        <input type="email" id="viceCaptainEmail" required>

        <label>Vice-Captain Phone:</label>
        <input type="tel" id="viceCaptainPhone" placeholder="+91 or 10 digits">

        <label>Vice-Captain WhatsApp (10 digits):</label>
        <input type="text" id="viceCaptainWhatsapp" maxlength="10">

        <!-- Players -->
        <h2>Players (11-15 required)</h2>
        <div id="playersContainer"></div>
        <button type="button" class="btn" onclick="addPlayer()">+ Add Player</button>

        <!-- Payment -->
        <h2>Payment Receipt</h2>
        <label>Payment Receipt (PDF):</label>
        <input type="file" id="paymentReceiptFile" accept=".pdf">

        <br><br>
        <button type="submit" class="btn">Submit Registration</button>
    </form>

    <div id="message"></div>

    <script>
        // Initialize with 11 empty player fields
        function initializeForm() {
            for (let i = 0; i < 11; i++) {
                addPlayer();
            }
        }

        function addPlayer() {
            const container = document.getElementById('playersContainer');
            const playerCount = container.children.length + 1;
            
            const playerDiv = document.createElement('div');
            playerDiv.className = 'player-section';
            playerDiv.id = `player-${playerCount}`;
            
            playerDiv.innerHTML = `
                <h3>Player ${playerCount}</h3>
                <label>Name:</label>
                <input type="text" class="playerName" required>

                <label>Age:</label>
                <input type="number" class="playerAge" min="15" max="60" required>

                <label>Phone:</label>
                <input type="tel" class="playerPhone" placeholder="+91 or 10 digits">

                <label>Role:</label>
                <select class="playerRole" required>
                    <option value="">-- Select Role --</option>
                    <option value="Batsman">Batsman</option>
                    <option value="Bowler">Bowler</option>
                    <option value="All-Rounder">All-Rounder</option>
                    <option value="Wicket Keeper">Wicket Keeper</option>
                </select>

                <label>Aadhar (PDF):</label>
                <input type="file" class="playerAadhar" accept=".pdf">

                <label>Subscription (PDF):</label>
                <input type="file" class="playerSubscription" accept=".pdf">

                ${playerCount > 11 ? '<button type="button" onclick="removePlayer(\'' + 'player-' + playerCount + '\')">Remove Player</button>' : ''}
            `;
            
            container.appendChild(playerDiv);
        }

        function removePlayer(playerId) {
            const playerDiv = document.getElementById(playerId);
            playerDiv.remove();
        }

        // Convert file to base64
        async function fileToBase64(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.onload = () => resolve(reader.result);
                reader.onerror = reject;
                reader.readAsDataURL(file);
            });
        }

        // Handle form submission
        document.getElementById('registrationForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            try {
                // Get players data
                const playerElements = document.querySelectorAll('.player-section');
                const players = [];

                for (const playerDiv of playerElements) {
                    const name = playerDiv.querySelector('.playerName').value;
                    const age = parseInt(playerDiv.querySelector('.playerAge').value);
                    const phone = playerDiv.querySelector('.playerPhone').value;
                    const role = playerDiv.querySelector('.playerRole').value;
                    
                    let aadharFile = null;
                    let subscriptionFile = null;

                    const aadharInput = playerDiv.querySelector('.playerAadhar');
                    if (aadharInput.files.length > 0) {
                        aadharFile = await fileToBase64(aadharInput.files[0]);
                    }

                    const subscriptionInput = playerDiv.querySelector('.playerSubscription');
                    if (subscriptionInput.files.length > 0) {
                        subscriptionFile = await fileToBase64(subscriptionInput.files[0]);
                    }

                    players.push({
                        name,
                        age,
                        phone: phone || null,
                        role,
                        aadharFile,
                        subscriptionFile
                    });
                }

                // Validate player count
                if (players.length < 11 || players.length > 15) {
                    throw new Error('Team must have 11-15 players');
                }

                // Convert files
                let pastorLetter = null;
                const pastorInput = document.getElementById('pastorLetterFile');
                if (pastorInput.files.length > 0) {
                    pastorLetter = await fileToBase64(pastorInput.files[0]);
                }

                let paymentReceipt = null;
                const paymentInput = document.getElementById('paymentReceiptFile');
                if (paymentInput.files.length > 0) {
                    paymentReceipt = await fileToBase64(paymentInput.files[0]);
                }

                // Prepare request
                const requestData = {
                    churchName: document.getElementById('churchName').value,
                    teamName: document.getElementById('teamName').value,
                    pastorLetter,
                    captain: {
                        name: document.getElementById('captainName').value,
                        email: document.getElementById('captainEmail').value,
                        phone: document.getElementById('captainPhone').value || null,
                        whatsapp: document.getElementById('captainWhatsapp').value || null
                    },
                    viceCaptain: {
                        name: document.getElementById('viceCaptainName').value,
                        email: document.getElementById('viceCaptainEmail').value,
                        phone: document.getElementById('viceCaptainPhone').value || null,
                        whatsapp: document.getElementById('viceCaptainWhatsapp').value || null
                    },
                    players,
                    paymentReceipt
                };

                console.log('Sending request:', requestData);

                // Send to backend
                const response = await fetch('http://localhost:8000/register/team', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });

                const result = await response.json();

                if (response.ok) {
                    showMessage(`✅ Success! Team ID: ${result.data.team_id}`, 'success');
                    document.getElementById('registrationForm').reset();
                    document.getElementById('playersContainer').innerHTML = '';
                    initializeForm();
                } else {
                    showMessage(`❌ Error: ${result.detail || 'Registration failed'}`, 'error');
                }
            } catch (error) {
                showMessage(`❌ Error: ${error.message}`, 'error');
            }
        });

        function showMessage(text, type) {
            const messageDiv = document.getElementById('message');
            messageDiv.textContent = text;
            messageDiv.className = `message ${type}`;
        }

        // Initialize form on page load
        document.addEventListener('DOMContentLoaded', initializeForm);
    </script>
</body>
</html>
```

### 2. React Component Example

```jsx
import React, { useState } from 'react';
import axios from 'axios';

const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    churchName: '',
    teamName: '',
    captain: { name: '', email: '', phone: '', whatsapp: '' },
    viceCaptain: { name: '', email: '', phone: '', whatsapp: '' },
    players: Array(11).fill().map(() => ({ 
      name: '', age: '', phone: '', role: '' 
    }))
  });

  const [files, setFiles] = useState({
    pastorLetter: null,
    paymentReceipt: null,
    playerFiles: {}
  });

  const [message, setMessage] = useState('');

  const handleInputChange = (e, path) => {
    const { value } = e.target;
    const keys = path.split('.');
    
    setFormData(prev => {
      const newData = JSON.parse(JSON.stringify(prev));
      let obj = newData;
      
      for (let i = 0; i < keys.length - 1; i++) {
        obj = obj[keys[i]];
      }
      obj[keys[keys.length - 1]] = value;
      
      return newData;
    });
  };

  const handlePlayerChange = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      players: prev.players.map((p, i) => 
        i === index ? { ...p, [field]: value } : p
      )
    }));
  };

  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      // Validate
      if (formData.players.length < 11 || formData.players.length > 15) {
        setMessage('❌ Team must have 11-15 players');
        return;
      }

      // Convert files to base64
      let pastorLetter = null;
      if (files.pastorLetter) {
        pastorLetter = await fileToBase64(files.pastorLetter);
      }

      let paymentReceipt = null;
      if (files.paymentReceipt) {
        paymentReceipt = await fileToBase64(files.paymentReceipt);
      }

      // Convert player files
      const players = await Promise.all(
        formData.players.map(async (player) => ({
          ...player,
          aadharFile: files.playerFiles[`aadhar_${player.name}`] 
            ? await fileToBase64(files.playerFiles[`aadhar_${player.name}`])
            : null,
          subscriptionFile: files.playerFiles[`sub_${player.name}`]
            ? await fileToBase64(files.playerFiles[`sub_${player.name}`])
            : null
        }))
      );

      const requestData = {
        ...formData,
        players,
        pastorLetter,
        paymentReceipt
      };

      // Send request
      const response = await axios.post(
        'http://localhost:8000/register/team',
        requestData
      );

      setMessage(`✅ Success! Team ID: ${response.data.data.team_id}`);
      
      // Reset form
      setFormData({
        churchName: '',
        teamName: '',
        captain: { name: '', email: '', phone: '', whatsapp: '' },
        viceCaptain: { name: '', email: '', phone: '', whatsapp: '' },
        players: Array(11).fill().map(() => ({ 
          name: '', age: '', phone: '', role: '' 
        }))
      });

    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '50px auto' }}>
      <h1>🏏 ICCT26 Team Registration</h1>
      <form onSubmit={handleSubmit}>
        {/* Team Info */}
        <h2>Team Information</h2>
        <input
          type="text"
          placeholder="Church Name"
          value={formData.churchName}
          onChange={(e) => handleInputChange(e, 'churchName')}
          required
        />
        <input
          type="text"
          placeholder="Team Name"
          value={formData.teamName}
          onChange={(e) => handleInputChange(e, 'teamName')}
          required
        />
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFiles({...files, pastorLetter: e.target.files[0]})}
        />

        {/* Captain */}
        <h2>Captain</h2>
        <input
          type="text"
          placeholder="Captain Name"
          value={formData.captain.name}
          onChange={(e) => handleInputChange(e, 'captain.name')}
          required
        />
        <input
          type="email"
          placeholder="Captain Email"
          value={formData.captain.email}
          onChange={(e) => handleInputChange(e, 'captain.email')}
          required
        />

        {/* Vice-Captain */}
        <h2>Vice-Captain</h2>
        <input
          type="text"
          placeholder="Vice-Captain Name"
          value={formData.viceCaptain.name}
          onChange={(e) => handleInputChange(e, 'viceCaptain.name')}
          required
        />

        {/* Players */}
        <h2>Players (11-15)</h2>
        {formData.players.map((player, index) => (
          <div key={index} style={{ border: '1px solid #ddd', padding: '15px', margin: '10px 0' }}>
            <h3>Player {index + 1}</h3>
            <input
              type="text"
              placeholder="Player Name"
              value={player.name}
              onChange={(e) => handlePlayerChange(index, 'name', e.target.value)}
              required
            />
            <input
              type="number"
              placeholder="Age"
              min="15"
              max="60"
              value={player.age}
              onChange={(e) => handlePlayerChange(index, 'age', parseInt(e.target.value))}
              required
            />
            <select
              value={player.role}
              onChange={(e) => handlePlayerChange(index, 'role', e.target.value)}
              required
            >
              <option value="">Select Role</option>
              <option value="Batsman">Batsman</option>
              <option value="Bowler">Bowler</option>
              <option value="All-Rounder">All-Rounder</option>
              <option value="Wicket Keeper">Wicket Keeper</option>
            </select>
          </div>
        ))}

        <button type="submit">Submit Registration</button>
      </form>

      {message && (
        <div style={{
          marginTop: '20px',
          padding: '10px',
          borderRadius: '4px',
          background: message.includes('✅') ? '#d4edda' : '#f8d7da',
          color: message.includes('✅') ? '#155724' : '#721c24'
        }}>
          {message}
        </div>
      )}
    </div>
  );
};

export default RegistrationForm;
```

### 3. Vue.js Example

```vue
<template>
  <div class="container">
    <h1>🏏 ICCT26 Team Registration</h1>

    <form @submit.prevent="submitForm">
      <!-- Team Info -->
      <div class="section">
        <h2>Team Information</h2>
        <input v-model="form.churchName" placeholder="Church Name" required />
        <input v-model="form.teamName" placeholder="Team Name" required />
        <input type="file" accept=".pdf" @change="uploadPastorLetter" />
      </div>

      <!-- Captain -->
      <div class="section">
        <h2>Captain</h2>
        <input v-model="form.captain.name" placeholder="Name" required />
        <input v-model="form.captain.email" type="email" placeholder="Email" required />
        <input v-model="form.captain.phone" placeholder="Phone" />
        <input v-model="form.captain.whatsapp" placeholder="WhatsApp" maxlength="10" />
      </div>

      <!-- Vice-Captain -->
      <div class="section">
        <h2>Vice-Captain</h2>
        <input v-model="form.viceCaptain.name" placeholder="Name" required />
        <input v-model="form.viceCaptain.email" type="email" placeholder="Email" required />
      </div>

      <!-- Players -->
      <div class="section">
        <h2>Players (11-15)</h2>
        <div v-for="(player, index) in form.players" :key="index" class="player-card">
          <h3>Player {{ index + 1 }}</h3>
          <input v-model="player.name" placeholder="Name" required />
          <input v-model.number="player.age" type="number" placeholder="Age" required />
          <select v-model="player.role" required>
            <option value="">Select Role</option>
            <option value="Batsman">Batsman</option>
            <option value="Bowler">Bowler</option>
            <option value="All-Rounder">All-Rounder</option>
            <option value="Wicket Keeper">Wicket Keeper</option>
          </select>
        </div>
      </div>

      <button type="submit">Submit Registration</button>
    </form>

    <div v-if="message" :class="['message', message.type]">
      {{ message.text }}
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      form: {
        churchName: '',
        teamName: '',
        captain: { name: '', email: '', phone: '', whatsapp: '' },
        viceCaptain: { name: '', email: '', phone: '', whatsapp: '' },
        players: Array(11).fill().map(() => ({ 
          name: '', age: '', phone: '', role: '' 
        }))
      },
      message: null
    };
  },
  methods: {
    uploadPastorLetter(event) {
      this.pastorLetterFile = event.target.files[0];
    },
    async submitForm() {
      try {
        const response = await fetch('http://localhost:8000/register/team', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.form)
        });

        const result = await response.json();
        
        if (response.ok) {
          this.message = {
            type: 'success',
            text: `✅ Success! Team ID: ${result.data.team_id}`
          };
          this.resetForm();
        } else {
          this.message = {
            type: 'error',
            text: `❌ Error: ${result.detail}`
          };
        }
      } catch (error) {
        this.message = {
          type: 'error',
          text: `❌ Error: ${error.message}`
        };
      }
    },
    resetForm() {
      this.form = {
        churchName: '',
        teamName: '',
        captain: { name: '', email: '', phone: '', whatsapp: '' },
        viceCaptain: { name: '', email: '', phone: '', whatsapp: '' },
        players: Array(11).fill().map(() => ({ 
          name: '', age: '', phone: '', role: '' 
        }))
      };
    }
  }
};
</script>

<style scoped>
.container { max-width: 1000px; margin: 50px auto; }
.section { margin: 30px 0; }
input, select { display: block; width: 100%; padding: 8px; margin: 5px 0 15px; }
button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
.message { margin-top: 20px; padding: 10px; border-radius: 4px; }
.message.success { background: #d4edda; color: #155724; }
.message.error { background: #f8d7da; color: #721c24; }
</style>
```

---

## 🔌 cURL Testing

Test the API directly:

```bash
# Simple registration with curl
curl -X POST "http://localhost:8000/register/team" \
  -H "Content-Type: application/json" \
  -d '{
    "churchName": "CSI St. Peters",
    "teamName": "Warriors",
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
    "players": [
      {"name": "Player 1", "age": 25, "role": "Batsman"},
      {"name": "Player 2", "age": 26, "role": "Bowler"},
      {"name": "Player 3", "age": 27, "role": "All-Rounder"},
      {"name": "Player 4", "age": 28, "role": "Wicket Keeper"},
      {"name": "Player 5", "age": 24, "role": "Batsman"},
      {"name": "Player 6", "age": 25, "role": "Bowler"},
      {"name": "Player 7", "age": 26, "role": "All-Rounder"},
      {"name": "Player 8", "age": 27, "role": "Batsman"},
      {"name": "Player 9", "age": 28, "role": "Bowler"},
      {"name": "Player 10", "age": 24, "role": "All-Rounder"},
      {"name": "Player 11", "age": 25, "role": "Wicket Keeper"}
    ],
    "pastorLetter": null,
    "paymentReceipt": null
  }'
```

---

## ⚙️ CORS Configuration

Your backend already has CORS enabled. If you get CORS errors, add this to `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change for production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🔒 Security Notes for Frontend

### 1. Never send files as base64 in production (too large)
Instead, use multipart/form-data:

```python
# Backend modification for file upload
from fastapi import File, UploadFile

@app.post("/register/team/upload")
async def register_team_with_upload(
    churchName: str,
    teamName: str,
    captain_json: str,
    players_json: str,
    pastor_letter: UploadFile = File(None),
    payment_receipt: UploadFile = File(None)
):
    # Handle file uploads
    pass
```

### 2. Validate on frontend before sending
- Check file size (max 5MB recommended)
- Verify email format
- Ensure phone numbers are valid
- Check player count (11-15)

### 3. Use HTTPS in production
- Get SSL certificate
- Force HTTPS redirect

### 4. Rate limiting
Add rate limiting to prevent abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/register/team")
@limiter.limit("10/minute")
async def register_team(...):
    pass
```

---

## 🧪 Test the Connection

### Step 1: Start Backend
```bash
uvicorn main:app --reload --port 8000
```

### Step 2: Open Swagger UI
```
http://localhost:8000/docs
```

### Step 3: Try the endpoint
Click on `/register/team` → Click "Try it out" → Enter sample data → Execute

### Step 4: Check Response
You should see:
```json
{
  "success": true,
  "message": "Team registration successful",
  "data": {
    "team_id": "ICCT26-20251105143934",
    "team_name": "Warriors",
    "captain_name": "John Doe",
    "players_count": 11,
    "email_sent": true,
    "database_saved": true
  }
}
```

---

## 📋 Checklist for Frontend Integration

- [ ] Backend is running on `http://localhost:8000`
- [ ] Test the API at `/docs` (Swagger UI)
- [ ] Create frontend registration form
- [ ] Implement form validation
- [ ] Convert files to base64 or use multipart
- [ ] Send POST request to `http://localhost:8000/register/team`
- [ ] Display success/error messages
- [ ] Test with sample data
- [ ] Verify data in PostgreSQL database
- [ ] Handle email confirmations
- [ ] Set up CORS for your frontend domain

---

## 🚀 Next Steps

1. **Choose Frontend Framework**: Vanilla JS, React, Vue, Angular, etc.
2. **Create Registration Form**: Use examples above
3. **Test Connection**: Use Swagger UI or cURL
4. **Handle Responses**: Show success/error messages
5. **Connect to Database**: Verify data is saved
6. **Deploy**: Move to production with HTTPS

---

## 📞 Support

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Database Queries**: Check PostgreSQL for stored data
- **Email Logs**: Check console for SMTP status

**Your backend is ready! 🚀 Start building the frontend!**
