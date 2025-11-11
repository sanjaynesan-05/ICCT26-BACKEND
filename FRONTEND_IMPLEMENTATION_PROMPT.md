# 🎯 COMPLETE FRONTEND IMPLEMENTATION PROMPT

Copy this entire prompt and paste it into your frontend AI assistant (Claude/ChatGPT/GitHub Copilot) to implement the file upload and display features.

---

## 📋 COPY FROM HERE ⬇️

I'm building a team cricket registration form frontend. Here's what I need:

### **PROJECT CONTEXT:**
- Frontend Framework: React (or Vue/Angular if you prefer)
- Backend API: `https://icct26-backend.onrender.com`
- Files are stored as Base64 strings in the database
- Maximum file size: 5MB per file
- Supported formats:
  - Images: JPEG, PNG, GIF, WebP
  - PDFs: PDF files

### **DATA STRUCTURE:**

The registration form needs to collect:

```json
{
  "churchName": "String",
  "teamName": "String",
  "pastorLetter": "Base64 image string (data:image/jpeg;base64,...)",
  "paymentReceipt": "Base64 image string (data:image/png;base64,...)",
  "captain": {
    "name": "String",
    "phone": "String (10 digits)",
    "whatsapp": "String (10 digits)",
    "email": "String (valid email)"
  },
  "viceCaptain": {
    "name": "String",
    "phone": "String (10 digits)",
    "whatsapp": "String (10 digits)",
    "email": "String (valid email)"
  },
  "players": [
    {
      "name": "String",
      "age": "Number (18-40)",
      "phone": "String (10 digits)",
      "role": "String (Batsman/Bowler/All-rounder/Wicketkeeper)",
      "aadharFile": "Base64 PDF string (data:application/pdf;base64,...)",
      "subscriptionFile": "Base64 PDF string (data:application/pdf;base64,...)"
    }
    // ... 11 players total
  ]
}
```

### **REQUIRED FEATURES:**

#### **1. FILE UPLOAD FUNCTIONALITY**

For each file upload field, I need:

- **Input field** that accepts files
- **File validation** before upload:
  - Check file type (image or PDF based on field)
  - Check file size (max 5MB)
  - Show error message if validation fails
- **Convert to Base64** when file is selected
- **Preview** for images (show thumbnail after upload)
- **Upload indicator** for PDFs (show ✅ after upload)
- **File counter** showing file size in MB

**File fields needed:**
1. `pastorLetter` - Image file (JPEG/PNG/GIF/WebP)
2. `paymentReceipt` - Image file (JPEG/PNG/GIF/WebP)
3. For each player:
   - `aadharFile` - PDF file
   - `subscriptionFile` - PDF file

#### **2. FORM LAYOUT**

Structure the form as:

```
Team Registration Form
├─ Church Name (text input)
├─ Team Name (text input)
├─ Pastor Letter (file upload + preview)
├─ Payment Receipt (file upload + preview)
├─ Captain Section
│  ├─ Name
│  ├─ Phone
│  ├─ WhatsApp
│  └─ Email
├─ Vice Captain Section
│  ├─ Name
│  ├─ Phone
│  ├─ WhatsApp
│  └─ Email
├─ Players Section (11 players)
│  └─ For each player:
│     ├─ Player number (e.g., "Player 1")
│     ├─ Name
│     ├─ Age
│     ├─ Phone
│     ├─ Role (dropdown)
│     ├─ Aadhar Card (PDF upload + indicator)
│     └─ Subscription (PDF upload + indicator)
└─ Submit Button
```

#### **3. FORM SUBMISSION**

- **Validate all fields** before submission
- **Show loading state** during submission
- **Handle errors** from backend:
  - If validation error: Show field name and error message
  - If network error: Show user-friendly error message
- **Success handling**: Show success message with Team ID
- **Clear form** after successful submission (optional)

#### **4. DISPLAY TEAM DETAILS (OPTIONAL - BONUS)**

After registration succeeds, create a "View Team" page that:

- Fetches team data from: `GET https://icct26-backend.onrender.com/api/teams/{team_id}`
- Displays:
  - Team name and church name
  - Pastor Letter image (with download button)
  - Payment Receipt image (with download button)
  - Captain info
  - Vice Captain info
  - Player list with:
    - Aadhar Card PDF (with download button or embedded viewer)
    - Subscription PDF (with download button or embedded viewer)

### **ERROR HANDLING REQUIREMENTS:**

The backend returns errors in this format:
```json
{
  "success": false,
  "message": "Validation failed",
  "field": "churchName",
  "error_type": "validation_error",
  "details": "Field required",
  "status_code": 422
}
```

Your frontend should:
1. Check `response.ok` to see if request succeeded
2. If failed (422 or other error):
   - Extract the error message
   - Highlight the problematic field
   - Show the error in a user-friendly way
3. Log the full response for debugging

### **CODE REQUIREMENTS:**

Please create:

1. **RegistrationForm.jsx** (or .tsx)
   - Main form component
   - Handle all form state
   - File upload handlers
   - Form submission

2. **FileUpload.jsx** (or .tsx) - Reusable component
   - Accept file input
   - Validate file
   - Convert to Base64
   - Show preview/indicator
   - Pass Base64 back to parent

3. **Utility function** for Base64 conversion:
   ```javascript
   const convertFileToBase64 = (file) => {
     return new Promise((resolve, reject) => {
       const reader = new FileReader();
       reader.onload = () => resolve(reader.result);
       reader.onerror = reject;
       reader.readAsDataURL(file);
     });
   };
   ```

4. **API service** for registration:
   ```javascript
   const registerTeam = async (data) => {
     const response = await fetch(
       'https://icct26-backend.onrender.com/api/register/team',
       {
         method: 'POST',
         headers: { 'Content-Type': 'application/json' },
         body: JSON.stringify(data)
       }
     );
     return response.json();
   };
   ```

5. **Styling** - Professional UI with:
   - Clear sections
   - Good spacing
   - Responsive design (mobile-friendly)
   - Color-coded messages (green for success, red for errors)
   - Loading spinner during submission

### **VALIDATION RULES:**

Implement frontend validation for:

- **Church Name**: Required, not empty
- **Team Name**: Required, not empty
- **Pastor Letter**: Required, image file, max 5MB
- **Payment Receipt**: Required, image file, max 5MB
- **Captain Name**: Required, not empty
- **Captain Phone**: Required, 10 digits only
- **Captain WhatsApp**: Required, 10 digits only
- **Captain Email**: Required, valid email format
- **Vice Captain**: Same as captain
- **Player Name**: Required for all players
- **Player Age**: Required, number between 18-40
- **Player Phone**: Required, 10 digits only
- **Player Role**: Required, must be one of: Batsman, Bowler, All-rounder, Wicketkeeper
- **Player Aadhar**: Required, PDF file, max 5MB
- **Player Subscription**: Required, PDF file, max 5MB

### **USER EXPERIENCE:**

- **On page load**: Show empty form with 11 player slots
- **During file upload**: Show progress/spinner
- **After file select**: Show preview (images) or checkmark (PDFs)
- **During form submission**: Disable all inputs, show loading spinner, change button text to "Submitting..."
- **On success**: Show success message with Team ID, option to view team or register another
- **On error**: Show red error message with field name, allow user to correct and resubmit

### **RESPONSIVE DESIGN:**

- Mobile (< 768px): Single column, full-width inputs
- Tablet (768px - 1024px): Two columns for form fields
- Desktop (> 1024px): Organized layout with proper spacing

### **BONUS FEATURES (Optional):**

1. File upload progress percentage
2. Drag-and-drop file upload
3. Multiple file format support indication
4. Show file size after upload (e.g., "1.2 MB")
5. "View Team Details" page after registration
6. Team ID copy-to-clipboard button
7. Confirm before submitting (prevent accidental clicks)

---

## 📋 END OF PROMPT ⬇️

---

## 🎯 HOW TO USE THIS PROMPT:

### **Option 1: Use with GitHub Copilot (FREE)**
1. Create a new file: `RegistrationForm.jsx`
2. Paste this entire prompt as a comment at the top
3. Let Copilot generate the code
4. Review and adjust as needed

### **Option 2: Use with ChatGPT/Claude**
1. Copy the entire prompt above (from "COPY FROM HERE" to "END OF PROMPT")
2. Paste into ChatGPT/Claude chat
3. Request: "Generate a complete React component based on this prompt"
4. Ask for additional files (FileUpload.jsx, API service, etc.)

### **Option 3: Use with AI Code Generator**
1. Use any AI code generator (e.g., v0.dev, Replit AI)
2. Paste this prompt
3. Generate the complete solution

---

## ✅ WHAT YOU'LL GET:

After using this prompt with an AI assistant, you should have:

✅ **RegistrationForm.jsx** - Main form component  
✅ **FileUpload.jsx** - Reusable file upload component  
✅ **API service** - Backend integration  
✅ **Styling** - Professional CSS/Tailwind  
✅ **Error handling** - User-friendly error messages  
✅ **File validation** - Size, type, format checks  
✅ **Base64 conversion** - Automatic file encoding  
✅ **Form validation** - All field requirements  
✅ **Responsive design** - Mobile to desktop  
✅ **Loading states** - Better UX  

---

## 🚀 AFTER IMPLEMENTATION:

1. **Test locally** with your frontend dev server
2. **Test file uploads**:
   - Try uploading images (pastor letter, payment receipt)
   - Try uploading PDFs (aadhar, subscription)
   - Try submitting with all fields filled
3. **Check backend errors**:
   - Missing fields → should show error
   - Invalid email → should show error
   - File too large → should show error
4. **Verify successful registration**:
   - Check console for Team ID
   - Verify team appears in database (optional)

---

## 📱 QUICK START (If generating code yourself):

If you want to build it manually, here's the minimum code to get started:

### **Basic File Upload Handler**
```javascript
const handleFileUpload = async (e, fieldName) => {
  const file = e.target.files[0];
  if (!file) return;
  
  // Validate
  const validTypes = {
    image: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    pdf: ['application/pdf']
  };
  
  if (file.size > 5 * 1024 * 1024) {
    alert('File too large (max 5MB)');
    return;
  }
  
  // Convert to Base64
  const reader = new FileReader();
  reader.onload = (e) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: e.target.result
    }));
  };
  reader.readAsDataURL(file);
};
```

### **Basic Form Submission**
```javascript
const handleSubmit = async (e) => {
  e.preventDefault();
  
  try {
    const response = await fetch(
      'https://icct26-backend.onrender.com/api/register/team',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      }
    );
    
    const result = await response.json();
    
    if (response.ok) {
      alert(`Success! Team ID: ${result.data.team_id}`);
    } else {
      alert(`Error: ${result.message}\nField: ${result.field}`);
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Failed to submit');
  }
};
```

---

## 🔗 BACKEND API REFERENCE:

### **Register Team**
```
POST https://icct26-backend.onrender.com/api/register/team
Content-Type: application/json

Request: { churchName, teamName, pastorLetter, paymentReceipt, captain, viceCaptain, players }
Response: { success: true, message, data: { team_id, ... } }
```

### **Get Team Details** (for viewing after registration)
```
GET https://icct26-backend.onrender.com/api/teams/{team_id}

Response: { success: true, team: { ... }, players: [ ... ] }
```

---

## ❓ FREQUENTLY ASKED QUESTIONS:

**Q: What if file upload fails?**  
A: The backend validates files. If invalid, it returns a 422 error with details. Show this to the user.

**Q: Do I need to encode the file on the frontend?**  
A: Yes! Use `FileReader.readAsDataURL()` to get Base64. This creates a data URI string that you send to the backend.

**Q: What if the backend returns an error?**  
A: Check `response.ok`. If false, read `result.message` and `result.field` to show user what went wrong.

**Q: Can I use Tailwind CSS?**  
A: Yes! The prompt is framework-agnostic. Use any CSS framework you prefer.

**Q: How do I test file uploads locally?**  
A: Create test files (small images/PDFs), select them in the form, and submit. Check console for API responses.

---

## 📊 SUCCESS CRITERIA:

You'll know the implementation is complete when:

✅ Form displays all fields correctly  
✅ Can select and preview image files  
✅ Can select PDF files (shows checkmark)  
✅ All form fields validate before submission  
✅ Form submits to backend successfully  
✅ Backend returns 200 with Team ID  
✅ Console shows Team ID (copy for later use)  
✅ Can view team details using Team ID (optional bonus)  

---

**Ready to build?** 🚀 Use this prompt with your AI assistant now!
