# Court-Data Fetcher & Mini-Dashboard (Firefox)

## Target Court: Madras High Court
I chose to target the Principal Bench of the Madras High Court.

https://hcmadras.tn.gov.in/

---

## Quick Setup

This guide explains how to set up this **Court-Data Fetcher & Mini-Dashboard** with **Firefox** on a Linux system.

---

## 1️⃣ Install Tesseract OCR engine

```bash
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

---

## 2️⃣ Install GeckoDriver (For Firefox)

```bash
GECKO_VER=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest | grep tag_name | cut -d '"' -f 4)
wget https://github.com/mozilla/geckodriver/releases/download/$GECKO_VER/geckodriver-$GECKO_VER-linux64.tar.gz
tar -xvzf geckodriver-*.tar.gz
sudo mv geckodriver /usr/local/bin/

```

---

## 3️⃣ Clone the Repo
Clone the repo to a directory on your host machine:

---

## 4️⃣ Set up venv in your Working Directory
Get inside the Working Directory (called 'practice') and then:

```bash
python3 -m venv venv
```

Activate it:

```bash
source venv/bin/activate
```

---

## 5️⃣ Install other python dependencies

```bash
pip install -r requirements.txt

```

---

## 6️⃣ Make sure Postgres is either running on your host machine or in a container
Update the connection string in **database.py** accordingly.

Default connection string config variables:
(user name = postgres, 
POSTGRES_PASSWORD = password, 
database name = postgres)

```python
DATABASE_URL = "postgresql://postgres:password@localhost:5432/postgres"

```

---

## 7️⃣ Set up your Uvicorn Server
Run:
```bash
uvicorn main:app --reload --port 8000

```

Now your app will be available at http://localhost:8000

Note: PDF downloads will be saved in the Working Directory

---

## CAPTCHA Strategy

I made use of **Tesseract Open Source OCR Engine**, which is a machine learning model that can read text from simple image files. Fortunately, the target CAPTCHA were 6-digit numbers without excess convolution.

**Selenium** is used to enter details, screenshot the captcha, scrape the results and download the pdf.

---

## Sample Input Value(s)

1.
Case Type: WRIT PETITION (WP), 
Case Number: 1234, 
Case Year: 2025, 

2.
Case Type: WRIT PETITION (WP), 
Case Number: 1000, 
Case Year: 2025, 

---

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)