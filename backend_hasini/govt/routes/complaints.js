const express   = require('express');
const Complaint = require('../models/Complaint');
const { protect, adminOnly } = require('../middleware/auth');

const router = express.Router();

// GET /api/complaints  — list with optional filters
router.get('/', protect, async (req, res) => {
  try {
    const filter = {};
    if (req.query.status)   filter.status   = req.query.status;
    if (req.query.district) filter.district = req.query.district;
    if (req.query.type)     filter.type     = req.query.type;
    if (req.query.search)   filter.title    = { $regex: req.query.search, $options: 'i' };
    if (req.officer.role !== 'admin' && req.officer.district !== 'All')
      filter.district = req.officer.district;

    const complaints = await Complaint.find(filter)
      .populate('assignedTo', 'name initials designation district')
      .sort({ createdAt: -1 });

    res.json({ success: true, count: complaints.length, data: complaints });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// GET /api/complaints/stats  — dashboard metrics
router.get('/stats', protect, async (req, res) => {
  try {
    const [total, open, inProgress, resolved, fraud] = await Promise.all([
      Complaint.countDocuments(),
      Complaint.countDocuments({ status: 'open' }),
      Complaint.countDocuments({ status: 'in-progress' }),
      Complaint.countDocuments({ status: 'resolved' }),
      Complaint.countDocuments({ status: 'fraud' }),
    ]);
    const districtStats = await Complaint.aggregate([
      { $group: { _id: '$district', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
    ]);
    const typeStats = await Complaint.aggregate([
      { $group: { _id: '$type', count: { $sum: 1 } } },
      { $sort: { count: -1 } },
    ]);
    res.json({ success: true, data: { total, open, inProgress, resolved, fraud, districtStats, typeStats } });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// GET /api/complaints/:id
router.get('/:id', protect, async (req, res) => {
  try {
    const complaint = await Complaint.findOne({
      $or: [
        { _id: req.params.id.match(/^[a-f\d]{24}$/i) ? req.params.id : null },
        { complaintId: req.params.id },
      ],
    }).populate('assignedTo', 'name initials designation district');
    if (!complaint) return res.status(404).json({ success: false, message: 'Complaint not found' });
    res.json({ success: true, data: complaint });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// POST /api/complaints  — citizen submission, no auth
router.post('/', async (req, res) => {
  try {
    const { title, description, type, district, scheme, amount, complainant } = req.body;
    const complaint = await Complaint.create({ title, description, type, district, scheme, amount, complainant });
    res.status(201).json({ success: true, data: complaint });
  } catch (err) {
    res.status(400).json({ success: false, message: err.message });
  }
});

// PUT /api/complaints/:id/assign
router.put('/:id/assign', protect, async (req, res) => {
  try {
    const complaint = await Complaint.findByIdAndUpdate(
      req.params.id,
      { assignedTo: req.body.officerId, status: 'in-progress' },
      { new: true }
    ).populate('assignedTo', 'name initials designation');
    if (!complaint) return res.status(404).json({ success: false, message: 'Complaint not found' });
    res.json({ success: true, data: complaint });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// PUT /api/complaints/:id/status
router.put('/:id/status', protect, async (req, res) => {
  try {
    const { status } = req.body;
    if (!['open', 'in-progress', 'resolved', 'fraud'].includes(status))
      return res.status(400).json({ success: false, message: 'Invalid status' });
    const complaint = await Complaint.findByIdAndUpdate(req.params.id, { status }, { new: true })
      .populate('assignedTo', 'name initials');
    if (!complaint) return res.status(404).json({ success: false, message: 'Complaint not found' });
    res.json({ success: true, data: complaint });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// PUT /api/complaints/:id/remarks
router.put('/:id/remarks', protect, async (req, res) => {
  try {
    const complaint = await Complaint.findByIdAndUpdate(
      req.params.id, { remarks: req.body.remarks }, { new: true }
    );
    if (!complaint) return res.status(404).json({ success: false, message: 'Complaint not found' });
    res.json({ success: true, data: complaint });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

// DELETE /api/complaints/:id  — admin only
router.delete('/:id', protect, adminOnly, async (req, res) => {
  try {
    const complaint = await Complaint.findByIdAndDelete(req.params.id);
    if (!complaint) return res.status(404).json({ success: false, message: 'Complaint not found' });
    res.json({ success: true, message: 'Complaint deleted' });
  } catch (err) {
    res.status(500).json({ success: false, message: err.message });
  }
});

module.exports = router;
