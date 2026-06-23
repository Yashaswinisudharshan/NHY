const express = require('express');
const jwt     = require('jsonwebtoken');
const Officer = require('../models/Officer');
const { protect, adminOnly } = require('../middleware/auth');

const router = express.Router();

const generateToken = (id) => jwt.sign({ id }, process.env.JWT_SECRET, { expiresIn: '7d' });

// POST /api/auth/login
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password)
    return res.status(400).json({ success: false, message: 'Email and password required' });

  try {
    const officer = await Officer.findOne({ email }).select('+password');
    if (!officer || !(await officer.matchPassword(password)))
      return res.status(401).json({ success: false, message: 'Invalid credentials' });
    if (!officer.isActive)
      return res.status(403).json({ success: false, message: 'Account deactivated' });

    res.json({
      success: true,
      token: generateToken(officer._id),
      officer: {
        id: officer._id, name: officer.name, initials: officer.initials,
        email: officer.email, role: officer.role,
        designation: officer.designation, district: officer.district,
      },
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// POST /api/auth/register  (admin only)
router.post('/register', protect, adminOnly, async (req, res) => {
  const { name, email, password, role, designation, district } = req.body;
  try {
    if (await Officer.findOne({ email }))
      return res.status(400).json({ success: false, message: 'Email already registered' });

    const officer = await Officer.create({ name, email, password, role, designation, district });
    res.status(201).json({
      success: true,
      officer: { id: officer._id, name: officer.name, initials: officer.initials, email: officer.email, role: officer.role },
    });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// GET /api/auth/me
router.get('/me', protect, (req, res) => res.json({ success: true, officer: req.officer }));

module.exports = router;
