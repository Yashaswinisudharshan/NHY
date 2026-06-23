const mongoose = require('mongoose');

const complaintSchema = new mongoose.Schema(
  {
    complaintId:  { type: String, unique: true },
    title:        { type: String, required: true, trim: true },
    description:  { type: String, required: true },
    type:         { type: String, enum: ['Fake Billing', 'Bribery', 'Fund Misuse', 'Ghost Workers', 'Other'], required: true },
    district:     { type: String, enum: ['Hyderabad', 'Warangal', 'Karimnagar', 'Nizamabad', 'Other'], required: true },
    scheme:       { type: String, required: true, trim: true },
    amount:       { type: String, default: 'Unknown' },
    status:       { type: String, enum: ['open', 'in-progress', 'resolved', 'fraud'], default: 'open' },
    assignedTo:   { type: mongoose.Schema.Types.ObjectId, ref: 'Officer', default: null },
    remarks:      { type: String, default: '' },
    isPublic:     { type: Boolean, default: true },
    complainant:  {
      name:    { type: String, default: 'Anonymous' },
      contact: { type: String, default: '' },
    },
  },
  { timestamps: true }
);

// Auto-generate readable complaint ID
complaintSchema.pre('save', async function (next) {
  if (!this.complaintId) {
    const year  = new Date().getFullYear();
    const count = await mongoose.model('Complaint').countDocuments();
    this.complaintId = `CMP-${year}-${String(count + 1).padStart(3, '0')}`;
  }
  next();
});

module.exports = mongoose.model('Complaint', complaintSchema);
