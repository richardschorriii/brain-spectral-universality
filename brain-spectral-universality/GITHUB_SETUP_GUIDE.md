# STEP-BY-STEP GITHUB REPOSITORY SETUP

**Total time:** 10 minutes  
**Difficulty:** Easy - just clicking buttons!

---

## STEP 1: Create Repository on GitHub (3 minutes)

1. Go to: https://github.com/
2. Log in to your account (or create one if needed)
3. Click green "New" button (top left) OR click "+" menu > "New repository"
4. Fill in:
   - **Repository name:** `brain-spectral-universality`
   - **Description:** "Code and data for spectral universality in resting-state brain networks"
   - **Public** (select this - required for bioRxiv link)
   - **✓ Add a README file** (UNCHECK this - we have our own)
   - **Add .gitignore:** None (we have our own)
   - **Choose a license:** None (we have our own)
5. Click green "Create repository" button

**Result:** You now have an empty repository!

---

## STEP 2: Upload Files to Repository (5 minutes)

### **Option A: Web Upload (Easiest)**

1. On your new repository page, click "uploading an existing file"
2. Drag and drop ALL files from the `brain-spectral-universality` folder:
   - README.md
   - LICENSE
   - requirements.txt
   - .gitignore
   - All folders (code, data, figures, tables, manuscript, notebooks)
3. Scroll down, add commit message: "Initial commit - repository structure"
4. Click green "Commit changes" button

**Done!** Repository is live.

### **Option B: Git Command Line (If you know Git)**

```bash
cd /path/to/brain-spectral-universality
git init
git add .
git commit -m "Initial commit - repository structure"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/brain-spectral-universality.git
git push -u origin main
```

---

## STEP 3: Get Repository URL (1 minute)

1. Go to your repository: https://github.com/YOUR_USERNAME/brain-spectral-universality
2. Copy the URL - this is what you'll use in bioRxiv submission!

**Your URL:**
```
https://github.com/YOUR_USERNAME/brain-spectral-universality
```

---

## STEP 4: Update bioRxiv Submission (1 minute)

When submitting to bioRxiv Monday:

**In "Data Availability" section:**
```
Code and data available at:
https://github.com/YOUR_USERNAME/brain-spectral-universality

Raw EEG data from PhysioNet:
https://physionet.org/content/eegmmidb/1.0.0/
```

---

## WHAT YOU HAVE NOW

✓ Professional GitHub repository  
✓ Complete README with overview  
✓ Proper LICENSE (MIT)  
✓ Python requirements listed  
✓ Folder structure ready  
✓ .gitignore configured  
✓ Ready to add code/data later

---

## ADDING FILES LATER

**After bioRxiv submission, add:**

1. Analysis code (Python scripts)
2. Processed data (CSV files)
3. Figures (PNG and PDF)
4. Tables (CSV)
5. Jupyter notebooks (optional)

**How to add files later:**
1. Go to repository on GitHub
2. Navigate to folder (e.g., `code/`)
3. Click "Add file" > "Upload files"
4. Drag and drop files
5. Commit changes

**Or use Git command line to push updates**

---

## UPDATING THE README

**After you get your bioRxiv DOI:**

1. Go to README.md on GitHub
2. Click pencil icon (edit)
3. Replace `YOUR_DOI_HERE` with actual DOI
4. Replace `YOUR_USERNAME` with your GitHub username
5. Commit changes

---

## TROUBLESHOOTING

**Can't create repository?**
- Make sure you're logged in
- Make sure name doesn't conflict with existing repo

**Upload fails?**
- Files might be too large (>100 MB) - GitHub has limits
- Upload in batches if needed

**Don't have GitHub account?**
- Create one (free): https://github.com/join
- Takes 2 minutes

---

## AFTER REPOSITORY IS LIVE

**Share it!**
- Include in bioRxiv submission ✓
- Include in PLOS submission ✓
- Add to your CV
- Share on social media (optional)

---

**Questions?** GitHub has excellent documentation: https://docs.github.com/

**You've got this!** It's easier than it looks. 🚀
