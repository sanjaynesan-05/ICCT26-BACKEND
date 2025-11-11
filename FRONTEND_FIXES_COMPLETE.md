# 🔧 FRONTEND FIXES FOR BACKEND INTEGRATION

## Issues Found & Fixes

### **Issue 1: API Response Format Mismatch**
Your backend returns success responses with `data` field, but the frontend doesn't handle this properly.

### **Issue 2: Team ID Display**
The success modal generates a random Team ID, but should show the actual Team ID from backend response.

### **Issue 3: Error Handling**
Backend errors include `field`, `message`, and `details` - frontend should parse these better.

### **Issue 4: File Conversion**
Files are converted to Base64 correctly, but the payload structure needs minor adjustments.

---

## ✅ FIXED FILE #1: `services/api.ts`

```typescript
/**
 * API Service Layer
 * Centralized backend communication for the ICCT26 frontend
 */

import { API_CONFIG } from '../config/app.config'

export interface TeamRegistrationPayload {
  churchName: string
  teamName: string
  pastorLetter: string // Base64 string with data URI
  captain: {
    name: string
    phone: string
    whatsapp: string
    email: string
  }
  viceCaptain: {
    name: string
    phone: string
    whatsapp: string
    email: string
  }
  players: Array<{
    name: string
    age: number
    phone: string
    role: string
    aadharFile: string // Base64 string with data URI
    subscriptionFile: string // Base64 string with data URI
  }>
  paymentReceipt: string // Base64 string with data URI
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
  detail?: string
  field?: string
  error_type?: string
  status_code?: number
}

export interface TeamRegistrationResponse {
  success: boolean
  message: string
  data: {
    team_id: string
    church_name: string
    team_name: string
    created_at: string
    [key: string]: any
  }
}

class ApiService {
  private baseUrl: string

  constructor() {
    this.baseUrl = API_CONFIG.baseUrl
  }

  /**
   * Get the full API URL
   */
  private getUrl(endpoint: string): string {
    return `${this.baseUrl}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`
  }

  /**
   * Generic fetch wrapper with error handling
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = this.getUrl(endpoint)
    const defaultHeaders = {
      'Content-Type': 'application/json',
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      })

      const data = await response.json()

      if (!response.ok) {
        // Backend returns structured error responses
        const error = new Error()
        ;(error as any).status = response.status
        ;(error as any).data = data
        throw error
      }

      return data as T
    } catch (error) {
      // Better error messages for common issues
      let message = 'Network error'
      let backendError = null

      if (error instanceof TypeError) {
        if (error.message.includes('Failed to fetch')) {
          message = `Cannot reach backend at ${this.baseUrl}. Make sure:\n1. Backend is running on ${this.baseUrl}\n2. Backend has CORS enabled\n3. Check your .env file: VITE_API_URL=${this.baseUrl}`
        } else if (error.message.includes('CORS')) {
          message = `CORS Error: Backend at ${this.baseUrl} needs to allow requests from this origin. Contact backend administrator.`
        } else {
          message = error.message
        }
      } else if (error instanceof Error) {
        backendError = (error as any).data
        if (backendError?.message) {
          message = backendError.message
        } else {
          message = error.message
        }
      }

      console.error(`API Error [${endpoint}]:`, error, backendError)

      // Re-throw with structured error info
      const apiError = new Error(message)
      ;(apiError as any).backendData = backendError
      throw apiError
    }
  }

  /**
   * Register a team
   */
  async registerTeam(payload: TeamRegistrationPayload): Promise<TeamRegistrationResponse> {
    return this.request<TeamRegistrationResponse>('/api/register/team', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  }

  /**
   * Get team details by ID
   */
  async getTeamById(teamId: string): Promise<any> {
    return this.request(`/api/teams/${teamId}`)
  }

  /**
   * Get registration status
   */
  async getRegistrationStatus(): Promise<any> {
    return this.request('/status')
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<any> {
    return this.request('/health')
  }

  /**
   * Get all registered teams
   */
  async getAllTeams(): Promise<any> {
    return this.request('/api/teams')
  }

  /**
   * Admin: Get all registered teams
   */
  async getAdminTeams(): Promise<any> {
    return this.request('/admin/teams')
  }

  /**
   * Admin: Get team details by ID
   */
  async getAdminTeamById(teamId: string): Promise<any> {
    return this.request(`/admin/teams/${teamId}`)
  }

  /**
   * Admin: Get player details
   */
  async getPlayerById(playerId: string): Promise<any> {
    return this.request(`/admin/players/${playerId}`)
  }

  /**
   * Admin: Get all registrations (teams + players)
   */
  async getAllRegistrations(): Promise<any> {
    return this.request('/admin/registrations')
  }
}

export const apiService = new ApiService()
```

---

## ✅ FIXED FILE #2: `components/PlayerFormCard.tsx`

```typescript
import React from 'react'
import { X } from 'lucide-react'
import FileUpload from './FileUpload'

interface PlayerData {
  name: string
  age: number
  phone: string
  role: string
  aadharFile: File | null
  aadharFileBase64: string | null
  subscriptionFile: File | null
  subscriptionFileBase64: string | null
}

interface Props {
  playerNumber: number
  player: PlayerData
  onChange: (data: Partial<PlayerData>) => void
  onRemove?: () => void
  canRemove?: boolean
}

const PlayerFormCard: React.FC<Props> = ({
  playerNumber,
  player,
  onChange,
  onRemove,
  canRemove,
}) => {
  const handleAadharChange = (base64: string | null) => {
    onChange({
      aadharFileBase64: base64,
      aadharFile: base64 ? new File([], 'aadhar') : null,
    })
  }

  const handleSubscriptionChange = (base64: string | null) => {
    onChange({
      subscriptionFileBase64: base64,
      subscriptionFile: base64 ? new File([], 'subscription') : null,
    })
  }

  return (
    <div className="bg-white rounded-xl p-4 shadow">
      <div className="flex justify-between items-start">
        <h4 className="font-subheading font-semibold text-gray-900">
          Player {playerNumber}
        </h4>
        {canRemove && onRemove && (
          <button
            onClick={onRemove}
            className="text-gray-400 hover:text-red-500 transition-colors"
            aria-label="Remove player"
          >
            <X size={20} />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">
            Full Name *
          </label>
          <input
            type="text"
            value={player.name}
            onChange={(e) => onChange({ name: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Enter player name"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">
            Age (15-60) *
          </label>
          <input
            type="number"
            min={15}
            max={60}
            value={player.age}
            onChange={(e) => onChange({ age: Number(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">
            Phone (10 digits) *
          </label>
          <input
            type="tel"
            value={player.phone}
            onChange={(e) => onChange({ phone: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Enter 10-digit phone number"
            maxLength={10}
            required
          />
        </div>

        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">
            Role *
          </label>
          <select
            value={player.role}
            onChange={(e) => onChange({ role: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-primary"
            required
          >
            <option value="">Select Role</option>
            <option value="Batsman">Batsman</option>
            <option value="Bowler">Bowler</option>
            <option value="All-Rounder">All-Rounder</option>
            <option value="Wicket Keeper">Wicket Keeper</option>
          </select>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">
            Aadhar / ID Card (PDF/PNG/JPEG) *
          </label>
          <FileUpload
            file={player.aadharFile}
            onFileChange={handleAadharChange}
            accept=".pdf,.png,.jpg,.jpeg"
            placeholder="Upload Aadhar Card"
          />
        </div>

        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">
            Subscription / Consent Form (PDF/PNG/JPEG) *
          </label>
          <FileUpload
            file={player.subscriptionFile}
            onFileChange={handleSubscriptionChange}
            accept=".pdf,.png,.jpg,.jpeg"
            placeholder="Upload Subscription"
          />
        </div>
      </div>
    </div>
  )
}

export default PlayerFormCard
```

---

## ✅ FIXED FILE #3: `pages/Registration.tsx` (Key Changes Only)

Replace the `handleSubmit` function and success modal section with these fixed versions:

### **PART 1: Fix handleSubmit function**

Replace the existing `handleSubmit` with this:

```typescript
  const handleSubmit = async () => {
    setIsSubmitting(true)
    setConvertingFiles(false)
    setValidationError('')
    try {
      // Full-form validation
      if (!formData.churchName.trim()) throw new Error('Please select a church name')
      if (!formData.teamName.trim()) throw new Error('Please enter a team name')
      if (!formData.pastorLetterBase64) throw new Error('Please upload a church letter')

      if (!formData.captain.name.trim()) throw new Error('Please enter captain name')
      if (!formData.captain.phone.trim())
        throw new Error('Please enter captain phone number')
      if (
        !formData.captain.whatsapp.trim() ||
        formData.captain.whatsapp.length !== 10
      )
        throw new Error(
          'Please enter valid 10-digit WhatsApp number for captain'
        )
      if (!formData.captain.email.trim() || !formData.captain.email.includes('@'))
        throw new Error('Please enter valid email for captain')

      if (!formData.viceCaptain.name.trim())
        throw new Error('Please enter vice-captain name')
      if (!formData.viceCaptain.phone.trim())
        throw new Error('Please enter vice-captain phone number')
      if (
        !formData.viceCaptain.whatsapp.trim() ||
        formData.viceCaptain.whatsapp.length !== 10
      )
        throw new Error(
          'Please enter valid 10-digit WhatsApp number for vice-captain'
        )
      if (
        !formData.viceCaptain.email.trim() ||
        !formData.viceCaptain.email.includes('@')
      )
        throw new Error('Please enter valid email for vice-captain')

      // Players
      if (formData.players.length < 11 || formData.players.length > 15)
        throw new Error('Team must have between 11 and 15 players')

      formData.players.forEach((p, idx) => {
        if (!p.name.trim()) throw new Error(`Player ${idx + 1}: Please enter name`)
        if (p.age < 15 || p.age > 60)
          throw new Error(`Player ${idx + 1}: Age must be between 15 and 60`)
        if (!p.phone.trim())
          throw new Error(`Player ${idx + 1}: Please enter phone number`)
        if (!p.role) throw new Error(`Player ${idx + 1}: Please select a role`)
        if (!VALID_ROLES.includes(p.role))
          throw new Error(`Player ${idx + 1}: Invalid role '${p.role}'`)
        if (!p.aadharFileBase64)
          throw new Error(`Player ${idx + 1}: Please upload Aadhar/ID`)
        if (!p.subscriptionFileBase64)
          throw new Error(`Player ${idx + 1}: Please upload subscription/consent`)
      })

      if (!formData.paymentReceiptBase64)
        throw new Error('Please upload payment receipt')

      // Build payload with Base64 strings
      const payload = {
        churchName: formData.churchName,
        teamName: formData.teamName,
        pastorLetter: formData.pastorLetterBase64,
        captain: {
          name: formData.captain.name,
          phone: formData.captain.phone,
          whatsapp: formData.captain.whatsapp,
          email: formData.captain.email,
        },
        viceCaptain: {
          name: formData.viceCaptain.name,
          phone: formData.viceCaptain.phone,
          whatsapp: formData.viceCaptain.whatsapp,
          email: formData.viceCaptain.email,
        },
        players: formData.players.map((p) => ({
          name: p.name,
          age: p.age,
          phone: p.phone,
          role: p.role,
          aadharFile: p.aadharFileBase64,
          subscriptionFile: p.subscriptionFileBase64,
        })),
        paymentReceipt: formData.paymentReceiptBase64,
      }

      // Call API with proper error handling
      const response = await apiService.registerTeam(payload)

      // Extract Team ID from response
      if (response.success && response.data?.team_id) {
        // Store Team ID in state for success modal
        setFormData((prev) => ({
          ...prev,
          // Add temporary field to store team_id
          teamId: response.data.team_id,
        }))
        setShowSuccess(true)
      } else {
        throw new Error('Registration failed: Invalid response from server')
      }
    } catch (err: unknown) {
      console.error('Submit error (raw):', err)

      let message = 'Registration failed'
      let fieldName = ''

      // Handle API errors with structured format
      if (err instanceof Error) {
        const backendData = (err as any).backendData

        if (backendData) {
          // Backend returned structured error
          message = backendData.message || backendData.detail || err.message
          fieldName = backendData.field || ''

          // Format field name for display
          if (fieldName) {
            message = `${fieldName}: ${message}`
          }
        } else {
          // Frontend validation error
          message = err.message
        }
      } else {
        message = String(err)
      }

      setValidationError(message)
    } finally {
      setIsSubmitting(false)
      setConvertingFiles(false)
    }
  }
```

### **PART 2: Update FormData interface to include teamId**

Find this section:
```typescript
interface FormData {
  churchName: string
  teamName: string
  pastorLetter: File | null
  pastorLetterBase64: string | null
  captain: CaptainInfo
  viceCaptain: CaptainInfo
  players: PlayerData[]
  paymentReceipt: File | null
  paymentReceiptBase64: string | null
}
```

Replace with:
```typescript
interface FormData {
  churchName: string
  teamName: string
  pastorLetter: File | null
  pastorLetterBase64: string | null
  captain: CaptainInfo
  viceCaptain: CaptainInfo
  players: PlayerData[]
  paymentReceipt: File | null
  paymentReceiptBase64: string | null
  teamId?: string // Add this field to store Team ID from backend
}
```

### **PART 3: Fix Success Modal**

Replace the success modal section with this:

```typescript
      {/* Success Modal */}
      <AnimatePresence>
        {showSuccess && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4"
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="glass-card rounded-2xl p-8 max-w-md w-full text-center"
            >
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="w-12 h-12 text-green-600" />
              </div>

              <h2 className="font-heading text-4xl text-primary mb-2">
                🎉 Registration Successful!
              </h2>

              <p className="font-subheading text-gray-700 mb-6">
                Your team has been successfully registered for ICCT26
              </p>

              <div className="bg-accent/20 rounded-lg p-4 mb-6 border-2 border-accent">
                <p className="text-sm text-gray-600 mb-2">Your Team ID</p>
                <p className="font-heading text-2xl text-primary break-all">
                  {formData.teamId || 'ICCT26-XXXX'}
                </p>
                <p className="text-xs text-gray-600 mt-2">
                  Save this ID for future reference
                </p>
              </div>

              <div className="bg-blue-50 rounded-lg p-4 mb-6 border-l-4 border-primary">
                <p className="text-sm text-gray-700">
                  A confirmation email will be sent to the captain's email address shortly.
                </p>
              </div>

              <button
                onClick={() => {
                  setShowSuccess(false)
                  setCurrentStep(0)
                  setFormData({
                    churchName: '',
                    teamName: '',
                    pastorLetter: null,
                    pastorLetterBase64: null,
                    captain: { name: '', phone: '', whatsapp: '', email: '' },
                    viceCaptain: {
                      name: '',
                      phone: '',
                      whatsapp: '',
                      email: '',
                    },
                    players: Array.from({ length: 11 }).map(() => emptyPlayer()),
                    paymentReceipt: null,
                    paymentReceiptBase64: null,
                  })
                  setAcceptTerms(false)
                }}
                className="btn-gold w-full hover:scale-105 transition-transform"
              >
                Done
              </button>

              <button
                onClick={() => {
                  navigator.clipboard.writeText(formData.teamId || '')
                  alert('Team ID copied to clipboard!')
                }}
                className="mt-3 w-full px-4 py-2 border-2 border-primary text-primary rounded-lg font-semibold hover:bg-primary/5 transition-colors"
              >
                Copy Team ID
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
```

---

## 📋 Summary of Changes

### **api.ts Changes:**
✅ Added `TeamRegistrationResponse` interface matching backend response  
✅ Added error field parsing (`field`, `message`, `error_type`)  
✅ Better error handling for backend structured errors  
✅ Proper type safety for API responses  

### **PlayerFormCard.tsx Changes:**
✅ Better placeholder text  
✅ Improved focus states with ring styling  
✅ Clearer labels  
✅ Better phone number validation (maxLength={10})  
✅ Role option text matches backend validation  

### **Registration.tsx Changes:**
✅ Store actual Team ID from backend in `formData.teamId`  
✅ Display real Team ID in success modal  
✅ Better error parsing with field information  
✅ Copy-to-clipboard button for Team ID  
✅ Form reset after success  
✅ Better success modal messaging  
✅ Added confirmation message about email  

---

## 🚀 How to Apply These Changes

### **Option 1: Replace Individual Files**
1. Replace `src/services/api.ts` with the fixed version
2. Replace `src/components/PlayerFormCard.tsx` with the fixed version
3. Update `src/pages/Registration.tsx` with the new functions and modal

### **Option 2: Manual Updates**
If you prefer manual updates, apply these changes to your existing files:

1. In `api.ts`: Add the new interfaces and error handling
2. In `PlayerFormCard.tsx`: Update styling and labels
3. In `Registration.tsx`: Replace `handleSubmit` and success modal section

---

## ✅ Testing Checklist

After applying fixes, test:

- [ ] Fill out complete form with all required fields
- [ ] Upload images for pastor letter and payment receipt
- [ ] Upload PDFs for player aadhar and subscription files
- [ ] Submit form and verify Team ID is displayed in success modal
- [ ] Copy Team ID button works
- [ ] Form resets after success
- [ ] Error messages show correct field names
- [ ] Backend validations (email, phone format) trigger proper errors
- [ ] File size validation (5MB) works correctly

---

**All files are now aligned with your backend! 🚀**
