# 🚀 FastAPI Installation Guide for Sub-Agents

## 🎯 **PROBLEM SOLVED:**
This guide fixes the `pydantic.errors.ConfigError: unable to infer type for attribute "name"` and Rust compilation issues that all sub-agents were experiencing.

## 📋 **PREREQUISITES:**
- Windows 10/11
- Python 3.14+ installed
- PowerShell or Command Prompt

## 🛠️ **STEP-BY-STEP SOLUTION:**

### **Step 1: Install Rust Compiler**
```powershell
# Download Rust installer
Invoke-WebRequest -Uri "https://win.rustup.rs/x86_64" -OutFile "rustup-init.exe"

# Install Rust with default settings
.\rustup-init.exe --default-toolchain stable --profile default -y

# Add Cargo to PATH (if needed)
$env:PATH += ";$env:USERPROFILE\.cargo\bin"
```

### **Step 2: Install FastAPI (Pre-compiled Binary)**
```powershell
# Install FastAPI using pre-compiled wheels (avoids Rust compilation issues)
py -m pip install fastapi --only-binary=all

# Install other dependencies
py -m pip install uvicorn --only-binary=all
py -m pip install pydantic --only-binary=all
```

### **Step 3: Alternative Method (If Step 2 Fails)**
```powershell
# Force reinstall with specific versions
py -m pip install fastapi==0.116.1 pydantic==2.11.7 --force-reinstall --only-binary=all

# Or use minimal requirements
py -m pip install -r requirements_minimal.txt
```

### **Step 4: Test Installation**
```powershell
# Test if FastAPI imports work
py -c "import fastapi; print('✅ FastAPI installed successfully!')"

# Test if server starts
py run.py
```

## 🎯 **COMMON ISSUES & SOLUTIONS:**

### **Issue 1: "Cargo not found"**
**Solution:** Make sure Rust is installed and in PATH
```powershell
# Check if Rust is installed
rustc --version
cargo --version

# If not found, restart PowerShell or add to PATH manually
$env:PATH += ";$env:USERPROFILE\.cargo\bin"
```

### **Issue 2: "unable to infer type for attribute"**
**Solution:** Use pre-compiled binaries instead of source compilation
```powershell
py -m pip install fastapi --only-binary=all --force-reinstall
```

### **Issue 3: Port conflicts**
**Solution:** Use dynamic port finding (already implemented in run.py)
```powershell
# Server will automatically find available port
py run.py
```

## 🚀 **VERIFICATION CHECKLIST:**

- [ ] Rust compiler installed (`rustc --version`)
- [ ] Cargo available (`cargo --version`)
- [ ] FastAPI imports work (`import fastapi`)
- [ ] Server starts without errors (`py run.py`)
- [ ] API documentation accessible (`http://localhost:PORT/docs`)
- [ ] Health check works (`http://localhost:PORT/health`)

## 📝 **FOR SUB-AGENT DEVELOPERS:**

### **Baseball Agent:**
```powershell
cd C:\Users\himse\mlb_betting_system
# Follow steps 1-4 above
```

### **Football Agent:**
```powershell
cd C:\Users\himse\cfl_nfl_gold
# Follow steps 1-4 above
```

## 🎯 **YOLO MODE FALLBACK:**

If FastAPI still fails, the system will automatically fall back to YOLO HTTP server:
- ✅ Server still works
- ✅ Basic endpoints available
- ✅ Can continue development
- ✅ No blocking issues

## 📞 **SUPPORT:**

If issues persist:
1. Check PowerShell version (`$PSVersionTable`)
2. Verify Python version (`py --version`)
3. Check PATH environment (`$env:PATH`)
4. Try restarting PowerShell
5. Use YOLO mode as fallback

## 🎉 **SUCCESS INDICATORS:**

- Server starts on any available port
- No Pydantic errors in logs
- FastAPI documentation accessible
- Health check returns 200 OK
- All endpoints responding

---

**🎯 This guide was created after successfully fixing the MultiSportsBettingPlatform Head Agent. Use the same approach for all sub-agents!** 