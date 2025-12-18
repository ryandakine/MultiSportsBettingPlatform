# PRD: License Application System
## Product Requirements Document for Marketing Site Application & Backend Integration

---

## 🎯 **PROJECT OVERVIEW**

### **Objective:**
Create a license application system that collects sufficient information to vet applicants for the $10K betting platform license, while maintaining legal compliance and not requesting excessive personal information.

### **Key Constraint:**
- Must be thorough enough to filter quality applicants
- Must NOT ask for too much personal information (legally safe)
- Focus on betting-related qualifications, not personal life details
- Balance between vetting needs and privacy protection

---

## 📋 **REQUIREMENTS**

### **1. APPLICATION FORM FIELDS**

#### **Required Fields:**
- **Full Name** (string, required)
  - Purpose: Identification and communication
  - Legal: Standard business practice, no legal issues
  
- **Email Address** (string, required, validated)
  - Purpose: Primary communication channel
  - Legal: Standard business practice, no legal issues

#### **Optional Fields:**
- **Phone Number** (string, optional)
  - Purpose: Alternative contact method
  - Legal: Voluntary, no issues
  - Note: Marked as optional to reduce friction

#### **Betting-Related Questions (Optional but Recommended):**
- **Betting Experience** (text, optional)
  - Question: "Tell us about your betting experience (optional)"
  - Prompt: "How long have you been betting? What sports do you focus on? What's your typical betting approach?"
  - Purpose: Vetting for serious bettors vs. casual browsers
  - Legal: Voluntary, business-relevant, no legal issues
  - Max length: 500 characters (prevent excessive input)

- **Interest in Platform** (text, optional)
  - Question: "Why are you interested in this platform? (optional)"
  - Prompt: "What attracted you to this platform? What are you hoping to achieve?"
  - Purpose: Understand motivation and filter serious buyers
  - Legal: Voluntary, business-relevant, no legal issues
  - Max length: 500 characters

#### **Required Acknowledgment:**
- **Monero Payment Acknowledgment** (boolean, required)
  - Statement: "I understand that payment is via Monero (XMR) only. I've read the Monero payment guide and understand this is for privacy protection."
  - Purpose: Legal protection, ensure users understand payment method
  - Legal: Standard terms acknowledgment, no issues

---

### **2. WHAT NOT TO ASK (Legal Safety)**

#### **❌ Do NOT Ask:**
- Social Security Number
- Date of Birth
- Physical Address
- Employment details
- Income/financial information
- Criminal history
- Family information
- Personal life details unrelated to betting

#### **✅ Safe to Ask:**
- Name (for identification)
- Email (for communication)
- Phone (optional, for contact)
- Betting experience (relevant to product)
- Interest in platform (relevant to product)

**Rationale:** Only ask business-relevant information. Betting experience and interest are directly relevant to the product being sold. Personal life details are not necessary and could create legal issues.

---

### **3. BACKEND API REQUIREMENTS**

#### **Endpoint: POST /api/v1/applications/submit**

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-123-4567",  // optional
  "experience": "5 years betting, focus on MLB and NBA...",  // optional
  "interest": "Looking for systematic approach to betting...",  // optional
  "monero_acknowledged": true  // required
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "application_id": "app_abc123",
  "message": "Application submitted successfully. We'll review within 48 hours.",
  "status": "pending"
}
```

**Response (Error - 400):**
```json
{
  "success": false,
  "error": "Validation error",
  "details": {
    "email": "Invalid email format",
    "monero_acknowledged": "Must acknowledge Monero payment requirement"
  }
}
```

**Response (Error - 500):**
```json
{
  "success": false,
  "error": "Internal server error",
  "message": "Failed to submit application. Please try again."
}
```

---

### **4. DATABASE SCHEMA**

#### **Table: license_applications**

**Fields:**
- `id` (String, PK, UUID)
- `name` (String, required)
- `email` (String, required, indexed)
- `phone` (String, nullable)
- `experience` (Text, nullable)
- `interest` (Text, nullable)
- `status` (String, default: "pending", indexed)
  - Values: "pending", "approved", "rejected"
- `monero_acknowledged` (Boolean, default: false)
- `created_at` (DateTime, auto)
- `updated_at` (DateTime, auto)
- `reviewed_at` (DateTime, nullable)
- `review_notes` (Text, nullable)  // Admin notes
- `payment_status` (String, default: "not_started")
  - Values: "not_started", "pending", "completed"
- `license_key` (String, nullable, unique, indexed)  // Generated after payment

**Indexes:**
- `email` (for lookup)
- `status` (for filtering)
- `license_key` (for lookup)

---

### **5. VALIDATION RULES**

#### **Frontend Validation:**
- Name: Required, min 2 characters, max 100 characters
- Email: Required, valid email format, max 255 characters
- Phone: Optional, if provided, validate format (flexible - allow various formats)
- Experience: Optional, max 500 characters
- Interest: Optional, max 500 characters
- Monero acknowledgment: Required checkbox

#### **Backend Validation:**
- Same rules as frontend
- Additional: Check for duplicate email addresses
- Additional: Rate limiting (prevent spam)

---

### **6. APPLICATION REVIEW PROCESS**

#### **Status Flow:**
1. **pending** - Initial state after submission
2. **approved** - Admin approves application
3. **rejected** - Admin rejects application
4. After approval: Payment flow begins
5. After payment: License key generated

#### **Review Criteria (Admin Side):**
- Quality of responses (if provided)
- Seriousness of interest
- Betting experience (if provided)
- Red flags (spam, obviously fake, etc.)

**Note:** Review process is manual (admin reviews). No automated approval/rejection.

---

### **7. SECURITY REQUIREMENTS**

- **Rate Limiting:** Max 3 applications per email per 24 hours
- **Email Validation:** Verify email format, check for disposable email domains
- **Input Sanitization:** Sanitize all text inputs (prevent XSS)
- **SQL Injection Protection:** Use parameterized queries (SQLAlchemy handles this)
- **CORS:** Allow marketing site domain only
- **No PII Storage:** Don't store unnecessary personal information

---

### **8. INTEGRATION REQUIREMENTS**

#### **Frontend (Marketing Site):**
- Submit form data to `/api/v1/applications/submit`
- Handle success/error responses
- Show success message with application ID
- Store application ID in local state (for reference)

#### **Backend (FastAPI):**
- Create new route: `src/api/application_routes.py`
- Create database model: `src/db/models/application.py`
- Add route to main router
- Implement validation
- Store in database
- Return response

---

### **9. EMAIL NOTIFICATIONS**

#### **To Applicant (After Submission):**
- Subject: "Application Received - MultiSports Betting Platform"
- Content: 
  - Thank you for your interest
  - Application ID
  - Review timeline (48 hours)
  - Next steps

#### **To Admin (After Submission):**
- Subject: "New License Application - [Name]"
- Content:
  - Applicant name and email
  - Application ID
  - Link to review application
  - Experience/Interest fields (if provided)

---

### **10. LEGAL COMPLIANCE**

#### **Data Collection:**
- Collect only necessary business information
- No sensitive personal data (SSN, DOB, address)
- Clear purpose: License application for betting platform
- Voluntary fields clearly marked as optional

#### **Privacy:**
- Store data securely
- Don't share with third parties
- Allow data deletion (GDPR compliance if needed)
- Clear privacy policy link

#### **Terms:**
- Application does not guarantee license
- Review process is at sole discretion
- Payment required after approval
- NDA required before access

---

## 🎯 **SUCCESS CRITERIA**

### **Functional:**
- ✅ Application form submits successfully
- ✅ Data stored in database correctly
- ✅ Validation works (frontend and backend)
- ✅ Email notifications sent
- ✅ Application ID returned to user

### **Legal:**
- ✅ Only asks business-relevant information
- ✅ No excessive personal data collection
- ✅ Voluntary fields clearly marked
- ✅ Acknowledgment required for payment method

### **UX:**
- ✅ Clear form labels and placeholders
- ✅ Helpful error messages
- ✅ Success confirmation
- ✅ Reasonable field lengths (not overwhelming)

---

## 📝 **IMPLEMENTATION TASKS**

### **Phase 1: Database Model**
1. Create `src/db/models/application.py`
2. Define `LicenseApplication` model
3. Add to database initialization
4. Create migration

### **Phase 2: Backend API**
1. Create `src/api/application_routes.py`
2. Define Pydantic models for request/response
3. Implement validation logic
4. Implement database save
5. Add rate limiting
6. Add to main router

### **Phase 3: Frontend Integration**
1. Update `ApplicationForm.js` to call API
2. Handle API responses (success/error)
3. Show appropriate messages
4. Add loading states

### **Phase 4: Email Notifications**
1. Create email templates
2. Implement email sending (after submission)
3. Test email delivery

### **Phase 5: Testing**
1. Test form submission
2. Test validation (frontend and backend)
3. Test database storage
4. Test email notifications
5. Test rate limiting

---

## 🔒 **SECURITY CONSIDERATIONS**

- Rate limiting per email/IP
- Input sanitization
- SQL injection protection (SQLAlchemy)
- XSS prevention (sanitize inputs)
- CORS configuration
- Email validation
- Duplicate email check

---

## 📊 **METRICS TO TRACK**

- Applications submitted per day
- Application approval rate
- Average time to review
- Conversion rate (application → payment)
- Rejection reasons (for improvement)

---

## 🚀 **DEPLOYMENT CHECKLIST**

- [ ] Database model created and migrated
- [ ] Backend API endpoint working
- [ ] Frontend form connected to API
- [ ] Validation working (frontend and backend)
- [ ] Email notifications working
- [ ] Rate limiting configured
- [ ] CORS configured correctly
- [ ] Error handling implemented
- [ ] Success messages working
- [ ] Testing completed

---

**Status:** Ready for Implementation  
**Priority:** High  
**Estimated Effort:** 2-3 hours  
**Dependencies:** Database setup, Email service


