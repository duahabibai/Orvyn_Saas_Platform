# FTP Deployment Instructions

This directory contains configuration files for deploying the frontend to your hosting provider via FileZilla.

## 🚀 How to Import to FileZilla

1. Open **FileZilla**.
2. Go to **File > Import...**.
3. Select `orvyn-production.xml` from this directory.
4. The site "ORVYN Production (Brandless Digital)" will now appear in your **Site Manager**.
5. Update the `User` and `Password` in the Site Manager to connect.

## 📁 What to Upload

After running `npm run build` in the `frontend` directory, upload the contents of the `frontend/out/` folder to the remote server root (usually `public_html/` or `/`).

## ⚠️ Security Note

- **Never** commit your actual password to this file.
- The `orvyn-production.xml` file is currently a template.
