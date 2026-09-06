import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Mail, 
  Phone, 
  MapPin, 
  Clock, 
  Send, 
  CheckCircle, 
  AlertCircle, 
  Edit3, 
  ShieldCheck, 
  Globe, 
  Radio, 
  Sparkles,
  X,
  Save,
  Check
} from 'lucide-react';
import { BusinessInfo, ContactFormData, ContactValidationErrors } from '../types';

export const ContactScreen: React.FC = () => {
  // Business info state
  const [businessInfo, setBusinessInfo] = useState<BusinessInfo | null>(null);
  const [isLoadingInfo, setIsLoadingInfo] = useState<boolean>(true);
  const [isEditingBusinessInfo, setIsEditingBusinessInfo] = useState<boolean>(false);
  const [businessEditForm, setBusinessEditForm] = useState<Partial<BusinessInfo>>({});
  const [businessSaveError, setBusinessSaveError] = useState<string | null>(null);
  const [businessSaveSuccess, setBusinessSaveSuccess] = useState<string | null>(null);

  // Contact form state
  const [formData, setFormData] = useState<ContactFormData>({
    fullName: '',
    corporateEmail: '',
    companyName: '',
    phoneNumber: '',
    inquiryType: 'Voyage Chartering & What-If Simulation',
    cargoParcelClass: 'Panamax (60,000 - 95,000 MT)',
    urgency: 'Normal',
    message: '',
  });

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [validationErrors, setValidationErrors] = useState<ContactValidationErrors>({});
  const [serverGeneralError, setServerGeneralError] = useState<string | null>(null);
  const [submissionSuccessData, setSubmissionSuccessData] = useState<{
    referenceId: string;
    dispatchDesk: string;
    timestamp: string;
    estimatedResponseTime: string;
  } | null>(null);

  // Fetch current business info from the Express server
  const fetchBusinessInfo = async () => {
    try {
      setIsLoadingInfo(true);
      const res = await fetch('/api/business-info');
      const data = await res.json();
      if (data.success && data.data) {
        setBusinessInfo(data.data);
        setBusinessEditForm(data.data);
      }
    } catch (err) {
      console.error('Failed to fetch business info:', err);
    } finally {
      setIsLoadingInfo(false);
    }
  };

  useEffect(() => {
    fetchBusinessInfo();
  }, []);

  // Handle Contact Form Submit with SERVER-SIDE Validation
  const handleSubmitContact = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setValidationErrors({});
    setServerGeneralError(null);

    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setSubmissionSuccessData({
          referenceId: result.referenceId,
          dispatchDesk: result.dispatchDesk,
          timestamp: result.timestamp,
          estimatedResponseTime: result.estimatedResponseTime,
        });
        setFormData({
          fullName: '',
          corporateEmail: '',
          companyName: '',
          phoneNumber: '',
          inquiryType: 'Voyage Chartering & What-If Simulation',
          cargoParcelClass: 'Panamax (60,000 - 95,000 MT)',
          urgency: 'Normal',
          message: '',
        });
      } else {
        // Server validation failed
        if (result.errors) {
          setValidationErrors(result.errors);
        }
        setServerGeneralError(result.message || 'Server validation failed. Please check the inputs.');
      }
    } catch (err) {
      setServerGeneralError('Network error connecting to the FreightIQ dispatch server. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle Update Business Info Submit
  const handleUpdateBusinessInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusinessSaveError(null);
    setBusinessSaveSuccess(null);

    try {
      const response = await fetch('/api/business-info', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(businessEditForm),
      });

      const result = await response.json();

      if (response.ok && result.success) {
        setBusinessInfo(result.data);
        setBusinessSaveSuccess('Business information successfully updated and saved to server.');
        setTimeout(() => {
          setIsEditingBusinessInfo(false);
          setBusinessSaveSuccess(null);
        }, 1200);
      } else {
        setBusinessSaveError(result.message || 'Failed to update business information.');
      }
    } catch (err) {
      setBusinessSaveError('Server error while saving business information.');
    }
  };

  return (
    <div className="flex flex-col w-full max-w-3xl mx-auto px-4 sm:px-6 py-4 pb-28 gap-5">
      {/* Screen Title */}
      <div className="flex flex-col gap-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5 text-primary" />
            <h1 className="text-xl sm:text-2xl font-bold text-on-surface">
              Commercial Desk &amp; Business Information
            </h1>
          </div>
          <span className="text-[11px] font-mono bg-tertiary/15 text-tertiary border border-tertiary/30 px-2 py-0.5 rounded font-bold">
            24/7 WATCHKEEPING
          </span>
        </div>
        <p className="text-xs text-on-surface-variant">
          Enterprise voyage inquiries, demurrage dispute assistance, and verified corporate registry credentials
        </p>
      </div>

      {/* Business Information Display Card */}
      <div className="bg-surface-container rounded-2xl border border-surface-container-high p-4 sm:p-5 flex flex-col gap-4 shadow-md">
        <div className="flex items-start justify-between">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-base sm:text-lg font-bold text-on-surface">
                {businessInfo?.companyName || 'FreightIQ Global Maritime Analytics Ltd.'}
              </span>
              <span className="text-[10px] font-mono bg-surface-container-high text-secondary px-2 py-0.5 rounded border border-surface-container-highest font-semibold">
                {businessInfo?.tradingName || 'FreightIQ 2026'}
              </span>
            </div>
            <span className="text-xs font-mono text-tertiary mt-0.5">
              {businessInfo?.imoCompanyNumber || 'IMO 9842109 / BIMCO #48291'}
            </span>
          </div>

          <button
            onClick={() => {
              setBusinessEditForm(businessInfo || {});
              setIsEditingBusinessInfo(true);
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-container-low hover:bg-primary/20 hover:text-primary text-on-surface-variant text-xs font-semibold border border-surface-container-high transition-all"
            title="Edit and update business information"
          >
            <Edit3 className="w-3.5 h-3.5" />
            <span>Update Info</span>
          </button>
        </div>

        {/* Contact Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
          <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50 flex flex-col gap-1">
            <span className="text-[10px] font-mono text-on-surface-variant uppercase flex items-center gap-1">
              <MapPin className="w-3 h-3 text-primary" />
              Global Headquarters
            </span>
            <span className="text-on-surface font-medium leading-relaxed">
              {businessInfo?.headquarters.addressLine1}, {businessInfo?.headquarters.city} {businessInfo?.headquarters.postalCode}, {businessInfo?.headquarters.country}
            </span>
          </div>

          <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50 flex flex-col gap-1">
            <span className="text-[10px] font-mono text-on-surface-variant uppercase flex items-center gap-1">
              <Phone className="w-3 h-3 text-tertiary" />
              24/7 Operations Hotline
            </span>
            <span className="text-tertiary font-mono font-bold">
              {businessInfo?.contactChannels.emergency247OpsPhone}
            </span>
            <span className="text-on-surface-variant text-[11px]">
              Switchboard: {businessInfo?.contactChannels.primaryPhone}
            </span>
          </div>

          <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50 flex flex-col gap-1">
            <span className="text-[10px] font-mono text-on-surface-variant uppercase flex items-center gap-1">
              <Mail className="w-3 h-3 text-secondary" />
              Commercial Chartering Desk
            </span>
            <span className="text-primary font-mono font-semibold truncate">
              {businessInfo?.contactChannels.commercialCharteringEmail}
            </span>
            <span className="text-on-surface-variant text-[11px] truncate">
              Demurrage: {businessInfo?.contactChannels.operationsDemurrageEmail}
            </span>
          </div>

          <div className="bg-surface-container-low p-3 rounded-xl border border-surface-container-high/50 flex flex-col gap-1">
            <span className="text-[10px] font-mono text-on-surface-variant uppercase flex items-center gap-1">
              <Radio className="w-3 h-3 text-secondary" />
              Maritime Telemetry Callsign
            </span>
            <span className="text-on-surface font-mono font-medium">
              {businessInfo?.contactChannels.satelliteVhfCallsign}
            </span>
            <span className="text-on-surface-variant text-[11px]">
              {businessInfo?.operatingHours}
            </span>
          </div>
        </div>

        {/* Global Regional Desks */}
        <div className="border-t border-surface-container-high/40 pt-3">
          <span className="text-xs font-semibold text-on-surface block mb-2">
            Active Regional Fixing Desks
          </span>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {businessInfo?.globalDesks.map((desk) => (
              <div key={desk.hub} className="bg-surface-container-low p-2.5 rounded-lg border border-surface-container-high/40 text-[11px]">
                <div className="flex items-center justify-between font-mono font-bold text-on-surface mb-0.5">
                  <span>{desk.hub}</span>
                </div>
                <span className="text-on-surface-variant block truncate">{desk.dutyOfficer}</span>
                <div className="flex items-center justify-between text-[10px] font-mono mt-1 pt-1 border-t border-surface-container-highest">
                  <span className="text-secondary">{desk.timezone}</span>
                  <span className="text-tertiary font-semibold">{desk.activeStatus}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Contact Form with SERVER-SIDE Validation */}
      <div className="bg-surface-container rounded-2xl border border-surface-container-high p-4 sm:p-5 flex flex-col gap-4 shadow-md">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Mail className="w-4 h-4 text-primary" />
            <h2 className="text-base sm:text-lg font-bold text-on-surface">
              Submit Chartering Inquiry or Fixture Query
            </h2>
          </div>
          <span className="text-[10px] font-mono text-secondary bg-surface-container-high px-2 py-0.5 rounded border border-surface-container-highest">
            SERVER VALIDATED
          </span>
        </div>

        {/* Success Alert Banner */}
        {submissionSuccessData && (
          <div className="bg-tertiary/15 border border-tertiary/40 rounded-xl p-4 flex flex-col gap-2 text-xs">
            <div className="flex items-center gap-2 text-tertiary font-bold text-sm">
              <CheckCircle className="w-5 h-5 shrink-0" />
              <span>Inquiry Successfully Logged on the Server!</span>
            </div>
            <p className="text-on-surface leading-relaxed">
              Your message has passed server-side verification and was routed to{' '}
              <strong className="text-primary font-mono">{submissionSuccessData.dispatchDesk}</strong>.
            </p>
            <div className="bg-surface-container-lowest/80 p-2.5 rounded-lg border border-surface-container-high/60 font-mono text-[11px] grid grid-cols-1 sm:grid-cols-2 gap-1.5 text-on-surface">
              <div>
                <span className="text-on-surface-variant">REFERENCE ID: </span>
                <strong className="text-tertiary">{submissionSuccessData.referenceId}</strong>
              </div>
              <div>
                <span className="text-on-surface-variant">TIMESTAMP: </span>
                <span>{new Date(submissionSuccessData.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="sm:col-span-2">
                <span className="text-on-surface-variant">ESTIMATED TURNAROUND: </span>
                <strong className="text-primary">{submissionSuccessData.estimatedResponseTime}</strong>
              </div>
            </div>
            <button
              onClick={() => setSubmissionSuccessData(null)}
              className="self-start text-[11px] font-mono text-tertiary underline mt-1 hover:text-white"
            >
              Submit another query
            </button>
          </div>
        )}

        {/* Server General Error Banner */}
        {serverGeneralError && (
          <div className="bg-error-container/25 border border-error/40 rounded-xl p-3 flex items-start gap-2 text-xs text-error">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <span className="leading-relaxed">{serverGeneralError}</span>
          </div>
        )}

        <form onSubmit={handleSubmitContact} className="flex flex-col gap-3.5">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Full Name */}
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-on-surface">
                Full Name <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                placeholder="Capt. Robert Evans"
                className={`w-full bg-surface-container-low border rounded-xl py-2 px-3 text-xs sm:text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none ${
                  validationErrors.fullName
                    ? 'border-error focus:border-error ring-1 ring-error/30'
                    : 'border-surface-container-high focus:border-primary'
                }`}
              />
              {validationErrors.fullName && (
                <span className="text-[11px] text-error font-medium">
                  {validationErrors.fullName}
                </span>
              )}
            </div>

            {/* Corporate Email */}
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-on-surface">
                Corporate Email <span className="text-error">*</span>
              </label>
              <input
                type="email"
                value={formData.corporateEmail}
                onChange={(e) => setFormData({ ...formData, corporateEmail: e.target.value })}
                placeholder="chartering@bulkmarine.com"
                className={`w-full bg-surface-container-low border rounded-xl py-2 px-3 text-xs sm:text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none ${
                  validationErrors.corporateEmail
                    ? 'border-error focus:border-error ring-1 ring-error/30'
                    : 'border-surface-container-high focus:border-primary'
                }`}
              />
              {validationErrors.corporateEmail && (
                <span className="text-[11px] text-error font-medium">
                  {validationErrors.corporateEmail}
                </span>
              )}
            </div>

            {/* Company Name */}
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-on-surface">
                Company / Trading House <span className="text-error">*</span>
              </label>
              <input
                type="text"
                value={formData.companyName}
                onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
                placeholder="Global Commodity Traders Ltd"
                className={`w-full bg-surface-container-low border rounded-xl py-2 px-3 text-xs sm:text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none ${
                  validationErrors.companyName
                    ? 'border-error focus:border-error ring-1 ring-error/30'
                    : 'border-surface-container-high focus:border-primary'
                }`}
              />
              {validationErrors.companyName && (
                <span className="text-[11px] text-error font-medium">
                  {validationErrors.companyName}
                </span>
              )}
            </div>

            {/* Phone Number */}
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-on-surface">
                Phone Number (with Country Code) <span className="text-error">*</span>
              </label>
              <input
                type="tel"
                value={formData.phoneNumber}
                onChange={(e) => setFormData({ ...formData, phoneNumber: e.target.value })}
                placeholder="+65 6829 4400"
                className={`w-full bg-surface-container-low border rounded-xl py-2 px-3 text-xs sm:text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none ${
                  validationErrors.phoneNumber
                    ? 'border-error focus:border-error ring-1 ring-error/30'
                    : 'border-surface-container-high focus:border-primary'
                }`}
              />
              {validationErrors.phoneNumber && (
                <span className="text-[11px] text-error font-medium">
                  {validationErrors.phoneNumber}
                </span>
              )}
            </div>
          </div>

          {/* Inquiry Type & Parcel Class */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-on-surface">
                Inquiry Category <span className="text-error">*</span>
              </label>
              <select
                value={formData.inquiryType}
                onChange={(e) => setFormData({ ...formData, inquiryType: e.target.value })}
                className="w-full bg-surface-container-low border border-surface-container-high rounded-xl py-2 px-3 text-xs sm:text-sm text-on-surface focus:outline-none focus:border-primary cursor-pointer"
              >
                <option value="Voyage Chartering & What-If Simulation">Voyage Chartering & What-If Simulation</option>
                <option value="Demurrage & Legal Risk Guard (WIBON/WIPON)">Demurrage & Legal Risk Guard (WIBON/WIPON)</option>
                <option value="Fleet AIS Radar & Tracking License">Fleet AIS Radar & Tracking License</option>
                <option value="Bulk Freight Hedging & FFA Curves">Bulk Freight Hedging & FFA Curves</option>
                <option value="General Enterprise Partnership">General Enterprise Partnership</option>
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs font-semibold text-on-surface">
                Urgency Level
              </label>
              <select
                value={formData.urgency}
                onChange={(e) => setFormData({ ...formData, urgency: e.target.value })}
                className="w-full bg-surface-container-low border border-surface-container-high rounded-xl py-2 px-3 text-xs sm:text-sm text-on-surface focus:outline-none focus:border-primary cursor-pointer"
              >
                <option value="Normal">Normal (Response within 24h)</option>
                <option value="Expedited (<24h)">Expedited (Within 8 hours)</option>
                <option value="Urgent Laycan (<48h)">Urgent Laycan Fixing (Within 2 hours)</option>
              </select>
            </div>
          </div>

          {/* Message Details */}
          <div className="flex flex-col gap-1">
            <label className="text-xs font-semibold text-on-surface">
              Voyage &amp; Cargo Inquiry Details <span className="text-error">*</span>
            </label>
            <textarea
              rows={4}
              value={formData.message}
              onChange={(e) => setFormData({ ...formData, message: e.target.value })}
              placeholder="Describe your parcel volume, intended load/discharge laycan dates, draft constraints, or legal fixture stipulations..."
              className={`w-full bg-surface-container-low border rounded-xl py-2 px-3 text-xs sm:text-sm text-on-surface placeholder:text-on-surface-variant/60 focus:outline-none resize-none ${
                validationErrors.message
                  ? 'border-error focus:border-error ring-1 ring-error/30'
                  : 'border-surface-container-high focus:border-primary'
              }`}
            />
            <div className="flex items-center justify-between text-[11px]">
              {validationErrors.message ? (
                <span className="text-error font-medium">{validationErrors.message}</span>
              ) : (
                <span className="text-on-surface-variant">Min. 15 characters required for validation.</span>
              )}
              <span className="font-mono text-on-surface-variant">{formData.message.length}/3000</span>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full py-3 rounded-xl bg-primary text-on-primary font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg hover:brightness-110 active:scale-[0.98] transition-all duration-150 disabled:opacity-75"
          >
            <Send className={`w-4 h-4 ${isSubmitting ? 'animate-spin' : ''}`} />
            <span>{isSubmitting ? 'Validating on FreightIQ Server...' : 'Submit Validated Inquiry'}</span>
          </button>
        </form>
      </div>

      {/* Edit Business Information Modal */}
      {isEditingBusinessInfo && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface-container border border-surface-container-high rounded-2xl max-w-xl w-full p-5 max-h-[90vh] overflow-y-auto flex flex-col gap-4 shadow-2xl animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-surface-container-high pb-3">
              <div className="flex items-center gap-2">
                <Edit3 className="w-5 h-5 text-primary" />
                <h3 className="text-base font-bold text-on-surface">
                  Update Corporate &amp; Business Information
                </h3>
              </div>
              <button
                onClick={() => setIsEditingBusinessInfo(false)}
                className="w-8 h-8 rounded-lg hover:bg-surface-container-high flex items-center justify-center text-on-surface-variant hover:text-on-surface"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {businessSaveError && (
              <div className="bg-error-container/20 border border-error/30 p-2.5 rounded-xl text-xs text-error">
                {businessSaveError}
              </div>
            )}

            {businessSaveSuccess && (
              <div className="bg-tertiary/20 border border-tertiary/40 p-2.5 rounded-xl text-xs text-tertiary font-semibold flex items-center gap-1.5">
                <Check className="w-4 h-4" />
                {businessSaveSuccess}
              </div>
            )}

            <form onSubmit={handleUpdateBusinessInfo} className="flex flex-col gap-3 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-on-surface">Company Registered Name</label>
                  <input
                    type="text"
                    value={businessEditForm.companyName || ''}
                    onChange={(e) => setBusinessEditForm({ ...businessEditForm, companyName: e.target.value })}
                    className="bg-surface-container-low border border-surface-container-high rounded-lg p-2 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-on-surface">IMO / BIMCO Number</label>
                  <input
                    type="text"
                    value={businessEditForm.imoCompanyNumber || ''}
                    onChange={(e) => setBusinessEditForm({ ...businessEditForm, imoCompanyNumber: e.target.value })}
                    className="bg-surface-container-low border border-surface-container-high rounded-lg p-2 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-on-surface">Commercial Chartering Email</label>
                  <input
                    type="email"
                    value={businessEditForm.contactChannels?.commercialCharteringEmail || ''}
                    onChange={(e) => setBusinessEditForm({
                      ...businessEditForm,
                      contactChannels: {
                        ...businessEditForm.contactChannels!,
                        commercialCharteringEmail: e.target.value,
                      }
                    })}
                    className="bg-surface-container-low border border-surface-container-high rounded-lg p-2 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-on-surface">Demurrage Operations Email</label>
                  <input
                    type="email"
                    value={businessEditForm.contactChannels?.operationsDemurrageEmail || ''}
                    onChange={(e) => setBusinessEditForm({
                      ...businessEditForm,
                      contactChannels: {
                        ...businessEditForm.contactChannels!,
                        operationsDemurrageEmail: e.target.value,
                      }
                    })}
                    className="bg-surface-container-low border border-surface-container-high rounded-lg p-2 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-on-surface">Switchboard Phone</label>
                  <input
                    type="text"
                    value={businessEditForm.contactChannels?.primaryPhone || ''}
                    onChange={(e) => setBusinessEditForm({
                      ...businessEditForm,
                      contactChannels: {
                        ...businessEditForm.contactChannels!,
                        primaryPhone: e.target.value,
                      }
                    })}
                    className="bg-surface-container-low border border-surface-container-high rounded-lg p-2 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>

                <div className="flex flex-col gap-1">
                  <label className="font-semibold text-on-surface">24/7 Watch Desk Emergency</label>
                  <input
                    type="text"
                    value={businessEditForm.contactChannels?.emergency247OpsPhone || ''}
                    onChange={(e) => setBusinessEditForm({
                      ...businessEditForm,
                      contactChannels: {
                        ...businessEditForm.contactChannels!,
                        emergency247OpsPhone: e.target.value,
                      }
                    })}
                    className="bg-surface-container-low border border-surface-container-high rounded-lg p-2 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>

                <div className="sm:col-span-2 flex flex-col gap-1">
                  <label className="font-semibold text-on-surface">Headquarters Address</label>
                  <input
                    type="text"
                    value={businessEditForm.headquarters?.addressLine1 || ''}
                    onChange={(e) => setBusinessEditForm({
                      ...businessEditForm,
                      headquarters: {
                        ...businessEditForm.headquarters!,
                        addressLine1: e.target.value,
                      }
                    })}
                    className="bg-surface-container-low border border-surface-container-high rounded-lg p-2 text-on-surface focus:outline-none focus:border-primary"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-surface-container-high">
                <button
                  type="button"
                  onClick={() => setIsEditingBusinessInfo(false)}
                  className="px-4 py-2 rounded-xl bg-surface-container-high text-on-surface hover:text-primary transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-primary text-on-primary font-semibold shadow hover:brightness-110 transition-all"
                >
                  <Save className="w-3.5 h-3.5" />
                  Save Business Info
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
