'use client'

import { useState } from 'react'
import { X, MapPin, AlertTriangle, Flame, Send } from 'lucide-react'

interface UserReportFormProps {
  isOpen: boolean
  onClose: () => void
  onSubmit: (reportData: UserReportData) => void
  loading?: boolean
}

export interface UserReportData {
  latitude: number
  longitude: number
  severity: 'Low' | 'Medium' | 'High' | 'Critical'
  description?: string
  reporter_name?: string
  reporter_contact?: string
  location_name?: string
  estimated_area?: number
  smoke_visibility?: 'None' | 'Light' | 'Moderate' | 'Heavy'
}

export default function UserReportForm({ isOpen, onClose, onSubmit, loading = false }: UserReportFormProps) {
  const [formData, setFormData] = useState<UserReportData>({
    latitude: 30.7333,
    longitude: 76.7794,
    severity: 'Medium',
    description: '',
    reporter_name: '',
    reporter_contact: '',
    location_name: '',
    estimated_area: undefined,
    smoke_visibility: 'Light'
  })

  const [errors, setErrors] = useState<{[key: string]: string}>({})
  const [step, setStep] = useState<'location' | 'details' | 'contact'>('location')

  if (!isOpen) return null

  const validateStep = (currentStep: string) => {
    const newErrors: {[key: string]: string} = {}

    if (currentStep === 'location') {
      if (!formData.latitude || formData.latitude < 20 || formData.latitude > 40) {
        newErrors.latitude = 'Please enter a valid latitude between 20 and 40'
      }
      if (!formData.longitude || formData.longitude < 68 || formData.longitude > 88) {
        newErrors.longitude = 'Please enter a valid longitude between 68 and 88'
      }
    }

    if (currentStep === 'details') {
      if (!formData.severity) {
        newErrors.severity = 'Please select severity level'
      }
      if (formData.estimated_area && (formData.estimated_area < 0 || formData.estimated_area > 1000)) {
        newErrors.estimated_area = 'Estimated area should be between 0 and 1000 hectares'
      }
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validateStep(step)) {
      if (step === 'location') setStep('details')
      else if (step === 'details') setStep('contact')
    }
  }

  const handleBack = () => {
    if (step === 'contact') setStep('details')
    else if (step === 'details') setStep('location')
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (validateStep('contact')) {
      onSubmit(formData)
    }
  }

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            latitude: Math.round(position.coords.latitude * 10000) / 10000,
            longitude: Math.round(position.coords.longitude * 10000) / 10000
          }))
        },
        (error) => {
          console.error('Error getting location:', error)
        }
      )
    }
  }

  return (
    <div 
      className="modal-overlay fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4"
      style={{ zIndex: 10000 }}
    >
      <div 
        className="modal-content bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto"
        style={{ zIndex: 10001 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-fire-red rounded-lg flex items-center justify-center">
              <Flame className="w-5 h-5 text-white" />
            </div>
            <h2 className="text-lg font-semibold text-charcoal">Report Stubble Burning</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Progress indicator */}
        <div className="px-6 py-4 border-b border-gray-100">
          <div className="flex items-center space-x-4">
            <div className={`flex items-center space-x-2 ${step === 'location' ? 'text-fire-red' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'location' ? 'bg-fire-red text-white' : 'bg-gray-200'
              }`}>1</div>
              <span className="text-sm font-medium">Location</span>
            </div>
            <div className="flex-1 h-px bg-gray-200"></div>
            <div className={`flex items-center space-x-2 ${step === 'details' ? 'text-fire-red' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'details' ? 'bg-fire-red text-white' : 'bg-gray-200'
              }`}>2</div>
              <span className="text-sm font-medium">Details</span>
            </div>
            <div className="flex-1 h-px bg-gray-200"></div>
            <div className={`flex items-center space-x-2 ${step === 'contact' ? 'text-fire-red' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                step === 'contact' ? 'bg-fire-red text-white' : 'bg-gray-200'
              }`}>3</div>
              <span className="text-sm font-medium">Contact</span>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {/* Step 1: Location */}
          {step === 'location' && (
            <div className="space-y-4">
              <div className="text-center mb-4">
                <MapPin className="w-12 h-12 text-fire-red mx-auto mb-2" />
                <h3 className="text-lg font-semibold text-charcoal">Where is the stubble burning?</h3>
                <p className="text-sm text-smoke-gray">Provide the exact location coordinates</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-charcoal mb-1">
                    Latitude <span className="text-fire-red">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={formData.latitude}
                    onChange={(e) => setFormData(prev => ({ ...prev, latitude: parseFloat(e.target.value) || 0 }))}
                    className={`input-field ${errors.latitude ? 'border-red-300' : ''}`}
                    placeholder="e.g., 30.7333"
                  />
                  {errors.latitude && <p className="text-sm text-red-600 mt-1">{errors.latitude}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-charcoal mb-1">
                    Longitude <span className="text-fire-red">*</span>
                  </label>
                  <input
                    type="number"
                    step="0.0001"
                    value={formData.longitude}
                    onChange={(e) => setFormData(prev => ({ ...prev, longitude: parseFloat(e.target.value) || 0 }))}
                    className={`input-field ${errors.longitude ? 'border-red-300' : ''}`}
                    placeholder="e.g., 76.7794"
                  />
                  {errors.longitude && <p className="text-sm text-red-600 mt-1">{errors.longitude}</p>}
                </div>

                <button
                  type="button"
                  onClick={getCurrentLocation}
                  className="w-full flex items-center justify-center space-x-2 py-2 px-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <MapPin className="w-4 h-4" />
                  <span>Use Current Location</span>
                </button>

                <div>
                  <label className="block text-sm font-medium text-charcoal mb-1">Location Name (Optional)</label>
                  <input
                    type="text"
                    value={formData.location_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, location_name: e.target.value }))}
                    className="input-field"
                    placeholder="e.g., Near Village XYZ, District ABC"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Fire Details */}
          {step === 'details' && (
            <div className="space-y-4">
              <div className="text-center mb-4">
                <AlertTriangle className="w-12 h-12 text-fire-orange mx-auto mb-2" />
                <h3 className="text-lg font-semibold text-charcoal">Fire Details</h3>
                <p className="text-sm text-smoke-gray">Describe the severity and characteristics</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-2">
                  Severity Level <span className="text-fire-red">*</span>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {(['Low', 'Medium', 'High', 'Critical'] as const).map((severity) => (
                    <button
                      key={severity}
                      type="button"
                      onClick={() => setFormData(prev => ({ ...prev, severity }))}
                      className={`p-3 rounded-lg border text-center transition-colors ${
                        formData.severity === severity
                          ? 'border-fire-red bg-fire-red/10 text-fire-red'
                          : 'border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className={`text-sm font-medium ${
                        severity === 'Critical' ? 'text-red-600' :
                        severity === 'High' ? 'text-orange-600' :
                        severity === 'Medium' ? 'text-yellow-600' : 'text-green-600'
                      }`}>
                        {severity}
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">Estimated Area (hectares)</label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="1000"
                  value={formData.estimated_area || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, estimated_area: e.target.value ? parseFloat(e.target.value) : undefined }))}
                  className={`input-field ${errors.estimated_area ? 'border-red-300' : ''}`}
                  placeholder="e.g., 2.5"
                />
                {errors.estimated_area && <p className="text-sm text-red-600 mt-1">{errors.estimated_area}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-2">Smoke Visibility</label>
                <select
                  value={formData.smoke_visibility}
                  onChange={(e) => setFormData(prev => ({ ...prev, smoke_visibility: e.target.value as any }))}
                  className="input-field"
                >
                  <option value="None">No visible smoke</option>
                  <option value="Light">Light smoke</option>
                  <option value="Moderate">Moderate smoke</option>
                  <option value="Heavy">Heavy smoke</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  className="input-field h-24 resize-none"
                  placeholder="Additional details about the fire incident..."
                />
              </div>
            </div>
          )}

          {/* Step 3: Contact Information */}
          {step === 'contact' && (
            <div className="space-y-4">
              <div className="text-center mb-4">
                <Send className="w-12 h-12 text-fire-yellow mx-auto mb-2" />
                <h3 className="text-lg font-semibold text-charcoal">Contact Information</h3>
                <p className="text-sm text-smoke-gray">Optional details for follow-up</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">Your Name (Optional)</label>
                <input
                  type="text"
                  value={formData.reporter_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, reporter_name: e.target.value }))}
                  className="input-field"
                  placeholder="Your full name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-charcoal mb-1">Contact (Optional)</label>
                <input
                  type="text"
                  value={formData.reporter_contact}
                  onChange={(e) => setFormData(prev => ({ ...prev, reporter_contact: e.target.value }))}
                  className="input-field"
                  placeholder="Phone number or email"
                />
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
                  <div>
                    <h4 className="text-sm font-medium text-yellow-800">Important Notice</h4>
                    <p className="text-sm text-yellow-700 mt-1">
                      Stubble burning is illegal and harmful to the environment and public health. 
                      This report will be shared with local authorities for appropriate action.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation buttons */}
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
            <button
              type="button"
              onClick={step === 'location' ? onClose : handleBack}
              className="px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 transition-colors"
            >
              {step === 'location' ? 'Cancel' : 'Back'}
            </button>

            {step !== 'contact' ? (
              <button
                type="button"
                onClick={handleNext}
                className="btn-primary"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                disabled={loading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Submitting...' : 'Submit Report'}
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}