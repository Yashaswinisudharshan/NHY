const mongoose = require('mongoose');
const bcrypt   = require('bcryptjs');

const officerSchema = new mongoose.Schema(
  {
    name:        { type: String, required: true, trim: true },
    initials:    { type: String, maxlength: 2 },
    email:       { type: String, required: true, unique: true, lowercase: true, trim: true },
    password:    { type: String, required: true, minlength: 6, select: false },
    role:        { type: String, enum: ['admin', 'officer', 'analyst'], default: 'officer' },
    designation: { type: String, default: '' },
    district:    { type: String, enum: ['Hyderabad', 'Warangal', 'Karimnagar', 'Nizamabad', 'All'], default: 'All' },
    isActive:    { type: Boolean, default: true },
  },
  { timestamps: true }
);

// Hash password before saving
officerSchema.pre('save', async function (next) {
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 10);
  if (!this.initials) {
    this.initials = this.name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
  }
  next();
});

officerSchema.methods.matchPassword = async function (entered) {
  return await bcrypt.compare(entered, this.password);
};

module.exports = mongoose.model('Officer', officerSchema);
