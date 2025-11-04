# Registration Form — Refactor Guide (Frontend)

This document contains a drop-in refactor for your React/TypeScript `Registration.tsx` and a companion `PlayerFormCard.tsx` update so the frontend sends the exact JSON structure your backend expects — nested `captain` and `viceCaptain` objects, `players` array with player-level files encoded as Base64, and other form changes (age, role, aadharFile, subscriptionFile).

Design and visual classes (Tailwind classes, framer-motion usage, icons) are preserved; only data structure and handlers change.

---

## What changed (high level)

- Captain and Vice-Captain are now nested objects: `captain: { name, phone, whatsapp, email }` and `viceCaptain: { ... }`.
- `players` is an array of objects: each player has `name`, `age` (15-60), `phone`, `role`, `aadharFile` (base64 string when submitted) and `subscriptionFile` (base64 string when submitted).
- Files (pastor letter, player files, payment receipt) are converted to Base64 before sending to backend.
- No visual/layout/tailwind changes.

---

## How to use this document

- Copy the `Registration.tsx` code into your frontend project replacing the existing file (or merge the parts you need).
- Copy the `PlayerFormCard.tsx` component (or adapt your current Player card) to accept `player` and `onChange` props.
- Keep your design/CSS; only logic/state is updated.

---

## Complete refactored Registration.tsx

Save as `Registration.tsx` in the same place your original file lives. This file preserves framer-motion, lucide icons and layout but updates the `FormData` shape, player handling, and submit logic.

```tsx
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'
import { Upload, Plus, CheckCircle, ChevronRight, ChevronLeft, X } from 'lucide-react'
import PlayerFormCard from '../components/PlayerFormCard'

interface CaptainInfo {
  name: string
  phone: string
  whatsapp: string
  email: string
}

interface PlayerData {
  name: string
  age: number
  phone: string
  role: string
  aadharFile: File | null
  subscriptionFile: File | null
}

interface FormData {
  churchName: string
  teamName: string
  pastorLetter: File | null
  captain: CaptainInfo
  viceCaptain: CaptainInfo
  players: PlayerData[]
  paymentReceipt: File | null
}

const CHURCH_NAMES = [
  "CSI St. Peter's Church",
  'CSI Christ Church',
  'CSI Grace Church',
  'CSI Zion Church',
  'CSI Emmanuel Church',
  'CSI Trinity Church',
  'CSI Holy Cross Church',
  'CSI Bethel Church',
  'CSI Calvary Church',
  'CSI Vision Church',
]

const Registration = () => {
  const [currentStep, setCurrentStep] = useState(1)
  const [playerCount, setPlayerCount] = useState(11)
  const [showSuccess, setShowSuccess] = useState(false)
  const [paymentFileName, setPaymentFileName] = useState('')
  const [paymentDragActive, setPaymentDragActive] = useState(false)
  const [pastorLetterFileName, setPastorLetterFileName] = useState('')
  const [pastorLetterDragActive, setPastorLetterDragActive] = useState(false)

  const emptyPlayer = (): PlayerData => ({
    name: '',
    age: 18,
    phone: '',
    role: '',
    aadharFile: null,
    subscriptionFile: null,
  })

  const [formData, setFormData] = useState<FormData>({
    churchName: '',
    teamName: '',
    pastorLetter: null,
    captain: { name: '', phone: '', whatsapp: '', email: '' },
    viceCaptain: { name: '', phone: '', whatsapp: '', email: '' },
    players: Array.from({ length: 11 }).map(() => emptyPlayer()),
    paymentReceipt: null,
  })

  const totalSteps = 5
  const progress = (currentStep / totalSteps) * 100

  const steps = [
    { number: 1, title: 'Team Details' },
    { number: 2, title: 'Captain & Vice-Captain' },
    { number: 3, title: 'Players' },
    { number: 4, title: 'Review' },
    { number: 5, title: 'Payment Upload' },
  ]

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1)
    } else {
      handleSubmit()
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) setCurrentStep(currentStep - 1)
  }

  // file handlers
  const handleFileChange = (file: File | null) => {
    setFormData({ ...formData, paymentReceipt: file })
    setPaymentFileName(file ? file.name : '')
  }

  const handlePastorLetterChange = (file: File | null) => {
    setFormData({ ...formData, pastorLetter: file })
    setPastorLetterFileName(file ? file.name : '')
  }

  const handlePaymentDragOver = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); setPaymentDragActive(true) }
  const handlePaymentDragLeave = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); setPaymentDragActive(false) }
  const handlePaymentDrop = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation(); setPaymentDragActive(false)
    const files = e.dataTransfer.files
    if (files && files[0]) handleFileChange(files[0])
  }

  const handlePastorLetterDragOver = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); setPastorLetterDragActive(true) }
  const handlePastorLetterDragLeave = (e: React.DragEvent) => { e.preventDefault(); e.stopPropagation(); setPastorLetterDragActive(false) }
  const handlePastorLetterDrop = (e: React.DragEvent) => {
    e.preventDefault(); e.stopPropagation(); setPastorLetterDragActive(false)
    const files = e.dataTransfer.files
    if (files && files[0]) handlePastorLetterChange(files[0])
  }

  // update single player
  const updatePlayer = (index: number, data: Partial<PlayerData>) => {
    const players = [...formData.players]
    players[index] = { ...players[index], ...data }
    setFormData({ ...formData, players })
  }

  // add / remove players
  const addPlayer = () => {
    if (playerCount < 15) {
      setFormData({ ...formData, players: [...formData.players, emptyPlayer()] })
      setPlayerCount(playerCount + 1)
    }
  }

  const removeLastPlayer = () => {
    if (playerCount > 11) {
      setFormData({ ...formData, players: formData.players.slice(0, -1) })
      setPlayerCount(playerCount - 1)
    }
  }

  // Base64 helper for files
  const toBase64 = (file: File) => new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result as string)
    reader.onerror = (err) => reject(err)
  })

  const handleSubmit = async () => {
    try {
      // Convert files to base64
      const pastorLetterBase64 = formData.pastorLetter ? await toBase64(formData.pastorLetter) : ''
      const paymentReceiptBase64 = formData.paymentReceipt ? await toBase64(formData.paymentReceipt) : ''

      const playersWithBase64 = await Promise.all(
        formData.players.map(async (player) => ({
          name: player.name,
          age: player.age,
          phone: player.phone,
          role: player.role,
          aadharFile: player.aadharFile ? await toBase64(player.aadharFile) : '',
          subscriptionFile: player.subscriptionFile ? await toBase64(player.subscriptionFile) : '',
        }))
      )

      const payload = {
        churchName: formData.churchName,
        teamName: formData.teamName,
        pastorLetter: pastorLetterBase64,
        captain: { ...formData.captain },
        viceCaptain: { ...formData.viceCaptain },
        players: playersWithBase64,
        paymentReceipt: paymentReceiptBase64,
      }

      const response = await fetch('http://localhost:8000/register/team', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (response.ok) {
        setShowSuccess(true)
      } else {
        const err = await response.json()
        alert(`Error: ${err.detail || 'Registration failed'}`)
      }
    } catch (err) {
      console.error('Submit error', err)
      alert('Failed to submit registration')
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="min-h-screen pt-32 pb-20 px-4 lg:px-8">
      <div className="container mx-auto max-w-6xl">
        {/* Header */}
        <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="text-center mb-12">
          <h1 className="font-heading text-6xl md:text-7xl text-accent mb-4">Team Registration</h1>
          <p className="font-subheading text-xl text-gray-300">Complete all steps to register your team</p>
        </motion.div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="h-3 bg-secondary/50 rounded-full overflow-hidden">
            <motion.div className="h-full bg-gradient-to-r from-primary via-accent to-accent" initial={{ width: 0 }} animate={{ width: `${progress}%` }} transition={{ duration: 0.5 }} />
          </div>
          <div className="flex justify-between mt-4">
            {steps.map((step) => (
              <div key={step.number} className={`flex flex-col items-center transition-all duration-300 ${currentStep >= step.number ? 'opacity-100' : 'opacity-40'}`}>
                <div className={`w-10 h-10 md:w-12 md:h-12 rounded-full flex items-center justify-center font-bold mb-2 transition-all duration-300 ${currentStep >= step.number ? 'bg-gradient-gold text-primary shadow-[0_0_20px_rgba(255,204,41,0.5)]' : 'bg-secondary text-gray-500'}`}>
                  {currentStep > step.number ? <CheckCircle className="w-6 h-6" /> : step.number}
                </div>
                <span className="text-xs md:text-sm font-subheading font-semibold text-white text-center hidden md:block">{step.title}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Form Container */}
        <div className="max-w-3xl mx-auto">
          <motion.div initial={{ x: 30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ delay: 0.3 }} className="glass-card rounded-2xl p-6 md:p-8">
            <AnimatePresence mode="wait">

              {/* Step 1: Team Details */}
              {currentStep === 1 && (
                <motion.div key="step1" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} transition={{ duration: 0.3 }}>
                  <h3 className="font-heading text-3xl text-primary mb-6">Team Information</h3>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Church Name *</label>
                      <select className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" value={formData.churchName} onChange={(e) => setFormData({ ...formData, churchName: e.target.value })} required>
                        <option value="">Select your church...</option>
                        {CHURCH_NAMES.map((church) => (<option key={church} value={church}>{church}</option>))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Team Name *</label>
                      <input type="text" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="Enter team name" value={formData.teamName} onChange={(e) => setFormData({ ...formData, teamName: e.target.value })} required />
                    </div>

                    <div>
                      <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Church Letter *</label>
                      <div className="relative">
                        <label className={`flex items-center gap-2 p-3 border-2 border-dashed rounded-lg cursor-pointer bg-white hover:shadow-md transition text-sm ${pastorLetterDragActive ? 'border-gray-700 bg-gray-100' : 'border-gray-300'}`} onDragOver={handlePastorLetterDragOver} onDragLeave={handlePastorLetterDragLeave} onDrop={handlePastorLetterDrop}>
                          <Upload className="w-5 h-5 text-gray-600" />
                          <span className="truncate max-w-[180px] text-gray-700 font-subheading">{pastorLetterFileName ? pastorLetterFileName : 'Upload Church Letter'}</span>
                          <input type="file" accept="image/*,.pdf,.doc,.docx" onChange={(e) => handlePastorLetterChange(e.target.files?.[0] || null)} className="hidden" />
                        </label>
                        {pastorLetterFileName && (<button type="button" className="absolute top-2 right-2 p-0.5 rounded-full bg-white hover:bg-gray-200 text-gray-500 shadow focus:outline-none focus:ring-2 focus:ring-gray-300" style={{ zIndex: 2, width: 18, height: 18, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={(e) => { e.stopPropagation(); handlePastorLetterChange(null) }} tabIndex={-1} aria-label="Cancel file upload"><X className="w-3 h-3" /></button>)}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Step 2: Captain & Vice-Captain */}
              {currentStep === 2 && (
                <motion.div key="step2" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} transition={{ duration: 0.3 }}>
                  <h3 className="font-heading text-3xl text-primary mb-6">Captain & Vice-Captain</h3>

                  <div className="space-y-8">
                    {/* Captain Details */}
                    <div className="bg-blue-50 rounded-xl p-6">
                      <h4 className="font-subheading font-bold text-primary text-xl mb-4">Captain Details</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Full Name *</label>
                          <input type="text" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="Captain's name" value={formData.captain.name} onChange={(e) => setFormData({ ...formData, captain: { ...formData.captain, name: e.target.value } })} required />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Phone Number *</label>
                            <input type="tel" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="+91 XXXXX XXXXX" value={formData.captain.phone} onChange={(e) => setFormData({ ...formData, captain: { ...formData.captain, phone: e.target.value } })} required />
                          </div>
                          <div>
                            <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">WhatsApp Number (10 digits) *</label>
                            <input type="tel" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="Enter 10-digit number" maxLength={10} value={formData.captain.whatsapp} onChange={(e) => setFormData({ ...formData, captain: { ...formData.captain, whatsapp: e.target.value } })} required />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Email *</label>
                          <input type="email" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="email@example.com" value={formData.captain.email} onChange={(e) => setFormData({ ...formData, captain: { ...formData.captain, email: e.target.value } })} required />
                        </div>
                      </div>
                    </div>

                    {/* Vice-Captain Details */}
                    <div className="bg-green-50 rounded-xl p-6">
                      <h4 className="font-subheading font-bold text-green-700 text-xl mb-4">Vice-Captain Details</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Full Name *</label>
                          <input type="text" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="Vice-Captain's name" value={formData.viceCaptain.name} onChange={(e) => setFormData({ ...formData, viceCaptain: { ...formData.viceCaptain, name: e.target.value } })} required />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Phone Number *</label>
                            <input type="tel" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="+91 XXXXX XXXXX" value={formData.viceCaptain.phone} onChange={(e) => setFormData({ ...formData, viceCaptain: { ...formData.viceCaptain, phone: e.target.value } })} required />
                          </div>
                          <div>
                            <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">WhatsApp Number (10 digits) *</label>
                            <input type="tel" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="Enter 10-digit number" maxLength={10} value={formData.viceCaptain.whatsapp} onChange={(e) => setFormData({ ...formData, viceCaptain: { ...formData.viceCaptain, whatsapp: e.target.value } })} required />
                          </div>
                        </div>

                        <div>
                          <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Email *</label>
                          <input type="email" className="w-full px-4 py-3 rounded-lg border-2 border-gray-300 input-focus text-gray-900" placeholder="email@example.com" value={formData.viceCaptain.email} onChange={(e) => setFormData({ ...formData, viceCaptain: { ...formData.viceCaptain, email: e.target.value } })} required />
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Step 3: Player Details */}
              {currentStep === 3 && (
                <motion.div key="step3" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} transition={{ duration: 0.3 }} className="max-h-[600px] overflow-y-auto overflow-x-hidden">
                  <div className="sticky top-0 bg-white pb-4 mb-4 z-10">
                    <h3 className="font-heading text-3xl text-primary mb-2">Player Details</h3>
                    <p className="text-sm text-gray-600">Add 11-15 players (Captain & Vice-Captain included)</p>
                  </div>

                  <div className="space-y-4">
                    {formData.players.map((player, index) => (
                      <PlayerFormCard key={index} playerNumber={index + 1} player={player} onChange={(data) => updatePlayer(index, data)} onRemove={index === formData.players.length - 1 && formData.players.length > 11 ? removeLastPlayer : undefined} canRemove={index === formData.players.length - 1 && formData.players.length > 11} />
                    ))}
                  </div>

                  {formData.players.length < 15 && (
                    <button onClick={addPlayer} className="w-full mt-6 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary to-primary hover:shadow-lg hover:shadow-primary/50 text-white font-subheading font-semibold rounded-lg transition-all duration-300 hover:scale-105">
                      <Plus className="w-5 h-5" />
                      Add Player
                    </button>
                  )}
                </motion.div>
              )}

              {/* Step 4: Review & Submit */}
              {currentStep === 4 && (
                <motion.div key="step4" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} transition={{ duration: 0.3 }}>
                  <h3 className="font-heading text-3xl text-primary mb-6">Review Information</h3>
                  <div className="space-y-6">
                    <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                      <p className="font-subheading text-green-700 font-semibold">✓ Please review all information before final submission</p>
                    </div>

                    <div className="space-y-3 text-gray-700">
                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Church Name:</span><span>{formData.churchName || 'N/A'}</span></div>
                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Team Name:</span><span>{formData.teamName || 'N/A'}</span></div>

                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Captain:</span><span>{formData.captain.name || 'N/A'}</span></div>
                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Captain Phone:</span><span>{formData.captain.phone || 'N/A'}</span></div>
                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Captain Email:</span><span>{formData.captain.email || 'N/A'}</span></div>

                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Vice-Captain:</span><span>{formData.viceCaptain.name || 'N/A'}</span></div>
                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Vice-Captain Phone:</span><span>{formData.viceCaptain.phone || 'N/A'}</span></div>
                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Vice-Captain Email:</span><span>{formData.viceCaptain.email || 'N/A'}</span></div>

                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Total Players:</span><span>{formData.players.length}</span></div>
                      <div className="flex justify-between py-2 border-b"><span className="font-subheading font-semibold">Registration Fee:</span><span className="text-green-600 font-bold">₹2,000</span></div>
                    </div>

                    <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded"><p className="text-sm text-yellow-800"><strong>Note:</strong> By submitting this form, you agree to the tournament rules and regulations. All information provided must be accurate.</p></div>
                  </div>
                </motion.div>
              )}

              {/* Step 5: Payment Upload */}
              {currentStep === 5 && (
                <motion.div key="step5" initial={{ opacity: 0, x: 50 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -50 }} transition={{ duration: 0.3 }}>
                  <h3 className="font-heading text-3xl text-primary mb-6">Payment Upload</h3>
                  <div className="space-y-6">
                    <div className="bg-blue-50 border-l-4 border-primary p-4 rounded"><p className="font-subheading text-primary font-semibold mb-2">Registration Fee: ₹2,000</p><p className="text-sm text-gray-700">Scan the QR code below to make payment</p></div>

                    <div className="flex flex-col items-center justify-center">
                      <div className="bg-white p-4 rounded-xl shadow-lg mb-4">
                        <img src="https://api.qrserver.com/v1/create-qr-code/?size=250x250&data=upi://pay?pa=icct26@upi&pn=ICCT26&am=2000&tn=ICCT26%20Registration%20Fee" alt="Payment QR Code" className="w-64 h-64 object-cover rounded-lg" />
                      </div>
                      <p className="text-center font-subheading text-gray-600 mb-4">Scan with any UPI app to pay ₹2,000</p>
                    </div>

                    <div>
                      <label className="block text-sm font-subheading font-semibold text-gray-700 mb-2">Upload Payment Receipt * (Required)</label>
                      <div className="relative">
                        <label className={`flex items-center gap-2 p-3 border-2 border-dashed rounded-lg cursor-pointer bg-white hover:shadow-md transition text-sm ${paymentDragActive ? 'border-gray-700 bg-gray-100' : 'border-gray-300'}`} onDragOver={handlePaymentDragOver} onDragLeave={handlePaymentDragLeave} onDrop={handlePaymentDrop}>
                          <Upload className="w-5 h-5 text-gray-600" />
                          <span className="truncate max-w-[180px] text-gray-700 font-subheading">{paymentFileName ? paymentFileName : 'Upload Receipt'}</span>
                          <input type="file" accept="image/*" onChange={(e) => handleFileChange(e.target.files?.[0] || null)} className="hidden" />
                        </label>
                        {paymentFileName && (<button type="button" className="absolute top-2 right-2 p-0.5 rounded-full bg-white hover:bg-gray-200 text-gray-500 shadow focus:outline-none focus:ring-2 focus:ring-gray-300" style={{ zIndex: 2, width: 18, height: 18, display: 'flex', alignItems: 'center', justifyContent: 'center' }} onClick={(e) => { e.stopPropagation(); handleFileChange(null) }} tabIndex={-1} aria-label="Cancel file upload"><X className="w-3 h-3" /></button>)}
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}

            </AnimatePresence>

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
              <button onClick={handlePrevious} disabled={currentStep === 1} className={`flex items-center gap-2 px-6 py-3 rounded-lg font-subheading font-semibold transition-all ${currentStep === 1 ? 'opacity-50 cursor-not-allowed bg-gray-200 text-gray-500' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}>
                <ChevronLeft className="w-5 h-5" /> Previous
              </button>

              <button onClick={handleNext} className="flex items-center gap-2 btn-gold">{currentStep === totalSteps ? 'Submit' : 'Next'}{currentStep < totalSteps && <ChevronRight className="w-5 h-5" />}</button>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Success Modal */}
      <AnimatePresence>
        {showSuccess && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 px-4">
            <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.8, opacity: 0 }} className="glass-card rounded-2xl p-8 max-w-md w-full text-center">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6"><CheckCircle className="w-12 h-12 text-green-600" /></div>
              <h2 className="font-heading text-4xl text-primary mb-4">Registration Successful!</h2>
              <p className="font-subheading text-gray-700 mb-6">Your team has been successfully registered for ICCT26</p>
              <div className="bg-accent/20 rounded-lg p-4 mb-6"><p className="text-sm text-gray-600 mb-2">Your Team ID</p><p className="font-heading text-3xl text-primary">ICCT26-{Math.floor(Math.random() * 10000).toString().padStart(4, '0')}</p></div>
              <button onClick={() => { setShowSuccess(false); setCurrentStep(1) }} className="btn-gold w-full">Close</button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

export default Registration
```

---

## Updated PlayerFormCard.tsx

This component now accepts `player` and `onChange` and emits field updates back to parent via `onChange(partialPlayerData)`.

```tsx
import React from 'react'
import { X } from 'lucide-react'

interface PlayerData {
  name: string
  age: number
  phone: string
  role: string
  aadharFile: File | null
  subscriptionFile: File | null
}

interface Props {
  playerNumber: number
  player: PlayerData
  onChange: (data: Partial<PlayerData>) => void
  onRemove?: () => void
  canRemove?: boolean
}

const PlayerFormCard: React.FC<Props> = ({ playerNumber, player, onChange, onRemove, canRemove }) => {
  const handleFile = (e: React.ChangeEvent<HTMLInputElement>, field: 'aadharFile' | 'subscriptionFile') => {
    const file = e.target.files?.[0] || null
    onChange({ [field]: file } as Partial<PlayerData>)
  }

  return (
    <div className="bg-white rounded-xl p-4 shadow">
      <div className="flex justify-between items-start">
        <h4 className="font-subheading font-semibold">Player {playerNumber}</h4>
        {canRemove && onRemove && (
          <button onClick={onRemove} className="text-gray-400 hover:text-red-500" aria-label="Remove player"><X /></button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">Full Name</label>
          <input type="text" value={player.name} onChange={(e) => onChange({ name: e.target.value })} className="w-full px-3 py-2 border rounded" />
        </div>

        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">Age</label>
          <input type="number" min={15} max={60} value={player.age} onChange={(e) => onChange({ age: Number(e.target.value) })} className="w-full px-3 py-2 border rounded" />
        </div>

        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">Phone</label>
          <input type="tel" value={player.phone} onChange={(e) => onChange({ phone: e.target.value })} className="w-full px-3 py-2 border rounded" />
        </div>

        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">Role</label>
          <select value={player.role} onChange={(e) => onChange({ role: e.target.value })} className="w-full px-3 py-2 border rounded">
            <option value="">Select Role</option>
            <option value="Batsman">Batsman</option>
            <option value="Bowler">Bowler</option>
            <option value="All-rounder">All-rounder</option>
            <option value="Wicket-keeper">Wicket-keeper</option>
          </select>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">Aadhar / ID (image/pdf)</label>
          <input type="file" accept="image/*,.pdf" onChange={(e) => handleFile(e, 'aadharFile')} />
          {player.aadharFile && <p className="text-xs text-gray-500 mt-1 truncate">{player.aadharFile.name}</p>}
        </div>

        <div>
          <label className="block text-sm font-subheading text-gray-700 mb-1">Subscription / Consent (image/pdf)</label>
          <input type="file" accept="image/*,.pdf" onChange={(e) => handleFile(e, 'subscriptionFile')} />
          {player.subscriptionFile && <p className="text-xs text-gray-500 mt-1 truncate">{player.subscriptionFile.name}</p>}
        </div>
      </div>
    </div>
  )
}

export default PlayerFormCard
```

---

## Integration notes

- Ensure `PlayerFormCard` is imported correctly in `Registration.tsx` (path: `../components/PlayerFormCard` in this doc). Adjust path if your project differs.
- `Registration.tsx` already converts uploaded files to Base64. The backend expects Base64 strings, so you don't need extra conversion server-side.
- The `players` array length is enforced on the backend (11–15). The UI limits adding/removing players to that range.
- Keep CORS and backend URL in mind if running frontend on a different origin than `http://localhost:8000`.

### Request payload example (after submit)

```json
{
  "churchName": "CSI St. Peter's Church",
  "teamName": "Spartans",
  "pastorLetter": "data:application/pdf;base64,...",
  "captain": { "name": "Alice", "phone": "+91...", "whatsapp":"...", "email":"..." },
  "viceCaptain": { "name": "Bob", "phone": "+91...", "whatsapp":"...", "email":"..." },
  "players": [ { "name":"P1","age":25,"phone":"...","role":"Batsman","aadharFile":"data:image/png;base64,...","subscriptionFile":"data:image/png;base64,..." }, ... ],
  "paymentReceipt": "data:image/jpeg;base64,..."
}
```

---

## Quick testing checklist

- [ ] Start backend (uvicorn) and ensure POST /register/team is reachable.
- [ ] Run the frontend and try a full registration with minimal valid data and image files.
- [ ] Check backend logs or responses for successful queueing and validation.
- [ ] If email/GoogleSheet integration is needed, set up backend credentials and test end-to-end.

---

## If you want me to apply these changes directly to a frontend repo

I can provide a git patch or open a PR if you share the frontend repo or give permission to edit. Right now this repo appears to be backend-only, so I created a document you can copy to the frontend workspace.

---

If you'd like, I can also:
- Provide a minimal `api-client.ts` helper to centralize backend URL and error handling.
- Add a small unit test that ensures `payload` shape before sending.

Let me know which next step you prefer.