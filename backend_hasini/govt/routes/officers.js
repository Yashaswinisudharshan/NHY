const express   = require('express');
const Officer   = require('../models/Officer');
const Complaint = require('../models/Complaint');
const { protect, adminOnly } = require('../middleware/auth');

const router = express.Router();

// GET /api/officers
router.get('/', protect, async (req, res) => {
  try {
    const officers = await Officer.find({ isActive: true }).select('-password');
    const officersWithStats = await Promise.all(
      officers.map(async (o) => {
        const [totalCases, fraudCases, resolved] = await Promise.all([
          Complaint.countDocuments({ assignedTo: o._id }),
          Complaint.countDocuments({ assignedTo: o._id, status: 'fraud' }),
          Complaint.countDocuments({ assignedTo: o._id, status: 'resolved' }),
        ]);
        return { ...o.toObject(), stats: { totalCases, fraudCases, resolved } };
      })
    );
    res.json({ success: true, count: officersWithStats.length, data: officersWithStats });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// GET /api/officers/:id
router.get('/:id', protect, async (req, res) => {
  try {
    const officer    = await Officer.findById(req.params.id).select('-password');
    if (!officer) return res.status(404).json({ success: false, message: 'Officer not found' });
    const complaints = await Complaint.find({ assignedTo: req.params.id })
      .select('complaintId title status district scheme createdAt').sort({ createdAt: -1 });
    res.json({ success: true, data: { officer, complaints } });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// PUT /api/officers/:id
router.put('/:id', protect, async (req, res) => {
  try {
    const isAdminOrSelf = req.officer.role === 'admin' || req.officer._id.toString() === req.params.id;
    if (!isAdminOrSelf) return res.status(403).json({ success: false, message: 'Not authorized' });
    if (req.body.role && req.officer.role !== 'admin') delete req.body.role;
    delete req.body.password;
    const officer = await Officer.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true }).select('-password');
    if (!officer) return res.status(404).json({ success: false, message: 'Officer not found' });
    res.json({ success: true, data: officer });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// DELETE /api/officers/:id  — soft delete
router.delete('/:id', protect, adminOnly, async (req, res) => {
  try {
    const officer = await Officer.findByIdAndUpdate(req.params.id, { isActive: false }, { new: true });
    if (!officer) return res.status(404).json({ success: false, message: 'Officer not found' });
    res.json({ success: true, message: `${officer.name} deactivated` });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
