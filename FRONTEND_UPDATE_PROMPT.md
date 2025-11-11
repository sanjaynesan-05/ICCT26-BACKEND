╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           FRONTEND UPDATE PROMPT - FILE UPLOAD RESTRICTIONS                ║
║                                                                            ║
║              Update Frontend to Support JPEG, PNG, PDF Only                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The backend has been updated to ONLY accept JPEG, PNG, and PDF files for all
file upload fields. This affects 4 file fields:

Team Level:
  - Pastor Letter
  - Payment Receipt

Player Level:
  - Aadhar File
  - Subscription File

All other file formats (GIF, WebP, JXL, etc.) will now be rejected with a 
validation error.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Update File Input Accept Attribute
   - All file inputs should accept ONLY: .jpg, .jpeg, .png, .pdf
   - This provides client-side validation and file picker filtering

2. Add Client-Side File Validation
   - Validate file extension before upload
   - Show user-friendly error messages
   - Prevent sending invalid files to backend

3. Show Clear Error Messages
   - Display which file types are allowed
   - Show current file type if user tries invalid format
   - Make it easy for users to fix their selection

4. Update File Upload Handlers
   - All file input handlers should validate format
   - Check file size (5MB max)
   - Display helpful error messages

5. Update Component Labels/Help Text
   - Specify file format requirements in UI
   - Help users understand what files are acceptable

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPLEMENTATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A. Update All File Input Elements

   Location: All file input fields in your React components
   
   Change FROM:
     <input type="file" onChange={handleFileUpload} />
   
   Change TO:
     <input 
       type="file" 
       accept=".jpg,.jpeg,.png,.pdf"
       onChange={handleFileUpload}
     />

   Files to Update:
     - PlayerFormCard.tsx (aadharFile, subscriptionFile)
     - Registration.tsx (pastorLetter, paymentReceipt)
     - Any other file input fields


B. Add File Validation Utility Function

   Create a new utility file: utils/fileValidation.ts
   
   Export these functions:
     1. isValidFileType(file: File): boolean
     2. getFileTypeError(file: File): string | null
     3. formatFileSizeError(maxSizeMB: number): string
     4. validateAndProcessFile(file: File): {valid: boolean, error?: string}

   Implementation:
     - Check file extension: .jpg, .jpeg, .png, .pdf
     - Check MIME type: image/jpeg, image/png, application/pdf
     - Check file size: max 5MB
     - Return error message if invalid


C. Update File Upload Handlers

   In each file upload handler:
   
   1. Validate file before processing
   2. Show error if validation fails
   3. Only convert to Base64 if validation passes
   4. Display error in UI (toast, alert, or form error)

   Example structure:
     const handleFileSelect = (event) => {
       const file = event.target.files[0];
       
       // Validate
       const validation = validateFile(file);
       if (!validation.valid) {
         setError(validation.error);
         return;
       }
       
       // Process
       convertToBase64(file);
       setError(null);
     };


D. Update Error Messages in Form

   When file validation fails, display:
   
   "❌ Invalid file format. Only JPEG (.jpg), PNG (.png), and PDF (.pdf) 
       files are allowed. You selected: [filename with extension]"

   Or for file size:
   
   "❌ File is too large. Maximum size is 5MB. Your file is [size]MB."


E. Update Component Help Text

   Add hint text below each file input:
   
   "Supported formats: JPEG (.jpg), PNG (.png), PDF (.pdf) | Max 5MB"

   Or with icon:
   
   "📎 Upload: JPEG, PNG, or PDF only (Max 5MB)"


F. Update TypeScript Types

   Update any types that reference file uploads:
   
   type AcceptedFileFormat = 'image/jpeg' | 'image/png' | 'application/pdf';
   type FileFieldName = 'pastorLetter' | 'paymentReceipt' | 
                        'aadharFile' | 'subscriptionFile';

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CODE EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Example 1: File Input Element

```tsx
// Before
<input 
  type="file" 
  onChange={handlePastorLetterUpload}
  className="w-full px-4 py-2 border border-gray-300 rounded"
/>

// After
<input 
  type="file" 
  accept=".jpg,.jpeg,.png,.pdf"
  onChange={handlePastorLetterUpload}
  className="w-full px-4 py-2 border border-gray-300 rounded"
/>
<p className="text-xs text-gray-600 mt-1">
  Supported: JPEG, PNG, PDF | Max 5MB
</p>
```


Example 2: File Validation Utility

```ts
// utils/fileValidation.ts

const ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf'];
const ALLOWED_MIMES = ['image/jpeg', 'image/png', 'application/pdf'];
const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export function isValidFileType(file: File): boolean {
  // Check MIME type
  if (!ALLOWED_MIMES.includes(file.type)) {
    return false;
  }

  // Check extension
  const ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return false;
  }

  return true;
}

export function getFileTypeError(file: File): string | null {
  if (!isValidFileType(file)) {
    return `Invalid file format: ${file.type || 'unknown'}. ` +
           `Only JPEG (.jpg), PNG (.png), and PDF (.pdf) are allowed.`;
  }
  return null;
}

export function getFileSizeError(file: File): string | null {
  if (file.size > MAX_FILE_SIZE_BYTES) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    return `File too large: ${sizeMB}MB. Maximum allowed: ${MAX_FILE_SIZE_MB}MB`;
  }
  return null;
}

export function validateFile(file: File): {valid: boolean, error?: string} {
  const typeError = getFileTypeError(file);
  if (typeError) {
    return { valid: false, error: typeError };
  }

  const sizeError = getFileSizeError(file);
  if (sizeError) {
    return { valid: false, error: sizeError };
  }

  return { valid: true };
}
```


Example 3: File Upload Handler

```tsx
// In PlayerFormCard.tsx or similar component

import { validateFile } from '@/utils/fileValidation';
import { FileReader as FR } from '@/utils/fileReader';

const handleAadharFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0];
  if (!file) return;

  // Validate file
  const validation = validateFile(file);
  if (!validation.valid) {
    setAadharError(validation.error || 'Invalid file');
    setPlayerData(prev => ({
      ...prev,
      aadharFile: undefined
    }));
    return;
  }

  // Process file
  try {
    const base64 = await FR.fileToBase64(file);
    setPlayerData(prev => ({
      ...prev,
      aadharFile: base64
    }));
    setAadharError(null); // Clear any previous errors
  } catch (error) {
    setAadharError('Failed to process file. Please try again.');
  }
};

// In JSX:
{aadharError && (
  <div className="text-red-500 text-sm mt-1">
    {aadharError}
  </div>
)}
```


Example 4: Full Component Update

```tsx
// PlayerFormCard.tsx - updated for file validation

import React, { useState } from 'react';
import { validateFile } from '@/utils/fileValidation';

interface PlayerFormProps {
  index: number;
  onUpdate: (data: any) => void;
}

export function PlayerFormCard({ index, onUpdate }: PlayerFormProps) {
  const [playerData, setPlayerData] = useState({
    name: '',
    age: '',
    phone: '',
    role: '',
    aadharFile: undefined,
    subscriptionFile: undefined,
  });

  const [errors, setErrors] = useState({
    aadhar: '',
    subscription: '',
  });

  const handleFileUpload = (fieldName: 'aadharFile' | 'subscriptionFile') => 
    async (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      // Validate
      const validation = validateFile(file);
      if (!validation.valid) {
        setErrors(prev => ({
          ...prev,
          [fieldName === 'aadharFile' ? 'aadhar' : 'subscription']: 
            validation.error || 'Invalid file'
        }));
        return;
      }

      // Convert to Base64
      try {
        const reader = new FileReader();
        reader.onload = () => {
          const base64 = reader.result as string;
          setPlayerData(prev => ({
            ...prev,
            [fieldName]: base64
          }));
          setErrors(prev => ({
            ...prev,
            [fieldName === 'aadharFile' ? 'aadhar' : 'subscription']: ''
          }));
          onUpdate(playerData);
        };
        reader.readAsDataURL(file);
      } catch (error) {
        setErrors(prev => ({
          ...prev,
          [fieldName === 'aadharFile' ? 'aadhar' : 'subscription']: 
            'Failed to process file'
        }));
      }
    };

  return (
    <div className="space-y-4">
      {/* Aadhar File */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Aadhar File
        </label>
        <input 
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFileUpload('aadharFile')}
          className="w-full px-4 py-2 border border-gray-300 rounded"
        />
        <p className="text-xs text-gray-600 mt-1">
          📎 Accepted: JPEG, PNG, PDF | Max 5MB
        </p>
        {errors.aadhar && (
          <div className="text-red-500 text-xs mt-1">
            ❌ {errors.aadhar}
          </div>
        )}
      </div>

      {/* Subscription File */}
      <div>
        <label className="block text-sm font-medium mb-1">
          Subscription File
        </label>
        <input 
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={handleFileUpload('subscriptionFile')}
          className="w-full px-4 py-2 border border-gray-300 rounded"
        />
        <p className="text-xs text-gray-600 mt-1">
          📎 Accepted: JPEG, PNG, PDF | Max 5MB
        </p>
        {errors.subscription && (
          <div className="text-red-500 text-xs mt-1">
            ❌ {errors.subscription}
          </div>
        )}
      </div>
    </div>
  );
}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILES TO UPDATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Priority 1 (Critical - Update First):
  ✓ Create: utils/fileValidation.ts
      - Add file validation utility functions
      - Export: isValidFileType, validateFile, getFileTypeError, getFileSizeError

  ✓ Update: components/PlayerFormCard.tsx
      - Add accept=".jpg,.jpeg,.png,.pdf" to aadharFile input
      - Add accept=".jpg,.jpeg,.png,.pdf" to subscriptionFile input
      - Add file validation on upload
      - Add error messages for invalid files
      - Add help text: "Accepted: JPEG, PNG, PDF | Max 5MB"

  ✓ Update: pages/Registration.tsx (or similar)
      - Add accept=".jpg,.jpeg,.png,.pdf" to pastorLetter input
      - Add accept=".jpg,.jpeg,.png,.pdf" to paymentReceipt input
      - Add file validation on upload
      - Add error messages for invalid files
      - Add help text: "Accepted: JPEG, PNG, PDF | Max 5MB"

Priority 2 (Nice to Have):
  ✓ Update: Any other components with file uploads
  ✓ Update: Existing file upload documentation
  ✓ Add: Toast/notification for file validation errors
  ✓ Add: File preview before upload (optional)

Priority 3 (Polish):
  ✓ Add: Loading state while converting Base64
  ✓ Add: File size indicator in UI
  ✓ Add: Success indicator when file is selected

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TESTING CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

After implementing updates, test these scenarios:

✓ Upload valid JPEG file
  - Should accept and show success
  - Should display file name or preview

✓ Upload valid PNG file
  - Should accept and show success
  - Should display file name or preview

✓ Upload valid PDF file
  - Should accept and show success
  - Should display file name or preview

✓ Upload invalid GIF file
  - Should show error message
  - Error should say "Only JPEG, PNG, PDF allowed"
  - Should prevent form submission

✓ Upload invalid WebP file
  - Should show error message
  - Error should say "Only JPEG, PNG, PDF allowed"

✓ Upload file larger than 5MB
  - Should show size error message
  - Should prevent submission

✓ Test on all file fields
  - pastorLetter: JPEG, PNG, PDF ✓
  - paymentReceipt: JPEG, PNG, PDF ✓
  - aadharFile: JPEG, PNG, PDF ✓
  - subscriptionFile: JPEG, PNG, PDF ✓

✓ Form submission after file upload
  - Should successfully submit with valid files
  - Should show backend validation errors if any

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MIGRATION GUIDE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If users previously uploaded GIF, WebP, or JXL files:

1. Communicate the change to users
2. Ask them to re-upload in JPEG or PNG format
3. Provide conversion tool or instructions:
   - "You can convert your image to JPEG/PNG using:"
     - Online: convertio.co, online-convert.com
     - Desktop: GIMP, Photoshop, Preview (Mac)
     - Command: ffmpeg, ImageMagick

4. For PDFs that were images:
   - Ask users to save as PDF or upload as image

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What to do:
  1. Create: utils/fileValidation.ts (copy from Example 2)
  2. Update: All file inputs with accept=".jpg,.jpeg,.png,.pdf"
  3. Add: File validation to all file handlers
  4. Display: Error messages for invalid files
  5. Test: All file formats and error scenarios

Timeline:
  - Small project: 30-60 minutes
  - Medium project: 1-2 hours
  - Large project: 2-4 hours

Status: READY FOR IMPLEMENTATION ✓

Backend Status: ✅ DEPLOYED (JPEG, PNG, PDF only)
Frontend Status: ⏳ AWAITING UPDATE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Questions? Check the examples above or ask for clarification!
