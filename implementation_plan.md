# RentEase - Complete Security, Authentication, Structure & Deployment Audit

A comprehensive review and hardening of the RentEase platform's security controls, authentication mechanisms, project structure, and deployment readiness.

## User Review Required

> [!IMPORTANT]
> To comply with modern Django security standards and DevSecOps best practices, we propose the following changes:
> 1. **Settings Reorganization**: We will split `RentEase/settings.py` into a modular package under `RentEase/settings/` (`base.py`, `development.py`, `production.py`).
> 2. **GET-based State Changes Mitigation**: We will refactor `toggle_wishlist` and `booking_action` from GET endpoints to POST endpoints. This protects the site against Cross-Site Request Forgery (CSRF) and accidental search engine pre-fetching. We will wrap the triggers in the templates inside clean HTML forms.
> 3. **Secret & Config Management**: We will introduce a `.env.example` file and configure Django to pull secrets (such as `SECRET_KEY`, `DATABASE_URL`, and debug settings) from environment variables.
> 4. **Upload File Limits**: We will add a validator to forms to enforce a maximum file upload size of 5MB to mitigate resource-exhaustion (DoS) risks.
> 5. **Git Ignored Assets**: We will create a `.gitignore` to ensure database files, local `.env` files, static assets, and media directories are not committed to source control.

---

## Proposed Changes

### Configuration & Settings Reorganization

#### [NEW] [base.py](file:///c:/rental_case_website/RentEase/settings/base.py)
Contains shared configurations (installed apps, middleware, template configurations, timezone setup, password validation rules).

#### [NEW] [development.py](file:///c:/rental_case_website/RentEase/settings/development.py)
Extends `base.py` for local developer work (enables `DEBUG = True`, uses local SQLite file, default console backend for mailers).

#### [NEW] [production.py](file:///c:/rental_case_website/RentEase/settings/production.py)
Extends `base.py` for production hosting (enables strict security headers, enforces SSL redirection, secures cookies, disables `DEBUG`).

#### [MODIFY] [manage.py](file:///c:/rental_case_website/manage.py)
#### [MODIFY] [wsgi.py](file:///c:/rental_case_website/RentEase/wsgi.py)
#### [MODIFY] [asgi.py](file:///c:/rental_case_website/RentEase/asgi.py)
Update default settings module path references to point to `RentEase.settings.development`.

#### [DELETE] [settings.py](file:///c:/rental_case_website/RentEase/settings.py)
Remove the original single settings file once split configuration is fully functional.

#### [NEW] [.env.example](file:///c:/rental_case_website/.env.example)
Clean configuration boilerplate with placeholder values for deployment.

#### [NEW] [.gitignore](file:///c:/rental_case_website/.gitignore)
Standard Python/Django git ignore rules including `.env`, `db.sqlite3`, `media/`, `staticfiles/`.

---

### Security Audits & View Hardening

#### [MODIFY] [views.py (wishlist)](file:///c:/rental_case_website/wishlist/views.py)
Restrict `toggle_wishlist` to require POST method using the `@require_POST` decorator.

#### [MODIFY] [views.py (bookings)](file:///c:/rental_case_website/bookings/views.py)
Restrict `booking_action` to require POST method using the `@require_POST` decorator.

#### [MODIFY] [forms.py (accounts)](file:///c:/rental_case_website/accounts/forms.py)
Add file size validators to user profile picture uploads.

#### [MODIFY] [forms.py (properties)](file:///c:/rental_case_website/properties/forms.py)
Add file size validators to property and gallery image uploads.

---

### Templates (Form & CSRF adjustments)

We will modify the templates containing wishlist triggers or booking action buttons to submit using CSRF-protected POST forms instead of anchor links:
- `home.html` (Featured properties wishlist trigger)
- `properties.html` (Catalog wishlist trigger)
- `property_detail.html` (Detail wishlist trigger)
- `my_wishlist.html` (Wishlist delete trigger)
- `owner_dashboard.html` (Approve/Reject buttons)

---

## Verification Plan

### Automated Verification
- Run code integrity check:
  ```bash
  python manage.py check
  ```
- Run production readiness check:
  ```bash
  python manage.py check --deploy
  ```
- Write and run unit tests for authentication & authorization:
  ```bash
  python manage.py test
  ```

### Manual Verification
- Verify that accessing `booking_action` or `toggle_wishlist` via GET URL raises a 405 error.
- Verify that wishlist heart toggles and approvals work seamlessly on the UI.
