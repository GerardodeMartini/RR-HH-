# Mensaje para Soporte de AWS SES (Añadir al ticket existente de Tienda Oceana)

**Instrucciones:** 
Copia el texto en inglés de abajo (AWS prioriza el inglés en su soporte técnico) y pégalo como una nueva "Respuesta" (Reply / Update) dentro de tu caso de soporte abierto. No abras un caso nuevo.

---

**[COPY AND PASTE THE FOLLOWING TEXT]**

Hello AWS Support Team,

I am writing to provide an update regarding my request to move my SES account out of the Sandbox.

Initially, I requested production access for my e-commerce project ("Tienda Oceana"). However, I would like to clarify that I will also be using this AWS account and SES region (Ohio) for a second project I am currently developing: **a Human Resources Platform**.

Since the Sandbox removal applies to the entire account, I want to be fully transparent about my complete use case for SES across both projects.

**Use Case Details for the New HR Platform:**

1. **How emails are obtained:** Users (either companies looking to hire, or professionals applying for vacancies) voluntarily register on our platform. The emails we collect are solely from these explicit, opt-in registrations.
2. **Types of emails sent (Strictly Transactional):**
   - Account creation and email verification links.
   - Password reset requests.
   - System notifications to candidates regarding updates to their application status.
   - Automated "re-engagement" emails sent to dormant candidates (inactive for > 6 months) asking if they want to remain active in our talent pool.
3. **What we DO NOT send:** We do not send marketing campaigns, newsletters, or cold emails of any kind.
4. **Bounce and Complaint Handling:** We will monitor the SES reputation dashboard and handle bounces/complaints to ensure we maintain a healthy sender reputation.

I have created separate SMTP IAM credentials for this new HR project to keep the access segregated from the e-commerce store. 

Please take this additional context into consideration for approving my entire account for production access.

Thank you for your time.
Best regards.

---

*(Fin del mensaje)*
