require('dotenv').config();
const mongoose  = require('mongoose');
const connectDB = require('./config/db');
const Officer   = require('./models/Officer');
const Complaint = require('./models/Complaint');

const officerSeedData = [
  { name: 'Rajesh Kumar',   email: 'admin@vigilanceiq.gov',  password: 'admin123',   role: 'admin',   designation: 'System Administrator',               district: 'All' },
  { name: 'Priya Sharma',   email: 'priya@vigilanceiq.gov',  password: 'officer123', role: 'officer', designation: 'District Inspector — Hyderabad',      district: 'Hyderabad' },
  { name: 'Anil Reddy',     email: 'anil@vigilanceiq.gov',   password: 'officer123', role: 'officer', designation: 'Vigilance Officer — Warangal',        district: 'Warangal' },
  { name: 'Meena Iyer',     email: 'meena@vigilanceiq.gov',  password: 'officer123', role: 'officer', designation: 'Anti-Corruption Officer — Karimnagar', district: 'Karimnagar' },
  { name: 'Suresh Babu',    email: 'suresh@vigilanceiq.gov', password: 'officer123', role: 'officer', designation: 'District Inspector — Nizamabad',      district: 'Nizamabad' },
  { name: 'Kavita Singh',   email: 'kavita@vigilanceiq.gov', password: 'officer123', role: 'analyst', designation: 'Fraud Analyst — Hyderabad',           district: 'Hyderabad' },
  { name: 'Ravi Naidu',     email: 'ravi@vigilanceiq.gov',   password: 'officer123', role: 'officer', designation: 'Vigilance Officer — Hyderabad',       district: 'Hyderabad' },
  { name: 'Deepa Rao',      email: 'deepa@vigilanceiq.gov',  password: 'officer123', role: 'officer', designation: 'Field Investigator — Warangal',       district: 'Warangal' },
  { name: 'Manoj Kulkarni', email: 'manoj@vigilanceiq.gov',  password: 'officer123', role: 'officer', designation: 'Anti-Corruption — Karimnagar',        district: 'Karimnagar' },
];

const seedDB = async () => {
  await connectDB();

  console.log('Clearing existing data...');
  await Officer.deleteMany();
  await Complaint.deleteMany();

  console.log('Seeding officers...');
  const createdOfficers = [];
  for (const data of officerSeedData) {
    const officer = await new Officer(data).save();
    createdOfficers.push(officer);
  }
  const byName = {};
  createdOfficers.forEach(o => byName[o.name] = o._id);

  console.log('Seeding complaints...');
  const complaintData = [
    { title: 'Inflated road repair bill in Kondapur',        description: 'Contractor submitted bill for 12km road repair but only 3km was done.',                type: 'Fake Billing',  district: 'Hyderabad',  scheme: 'MGNREGS',            amount: '₹8.4L',   status: 'fraud',       assignedTo: byName['Kavita Singh'],  remarks: '' },
    { title: 'Ghost workers in Warangal Aavas Yojana',       description: 'Payroll shows 47 workers but locals report only 18-20 people actually working.',         type: 'Ghost Workers', district: 'Warangal',   scheme: 'PM Awas Yojana',    amount: '₹2.1L',   status: 'in-progress', assignedTo: byName['Anil Reddy'],    remarks: '' },
    { title: 'Bribery demand for ration card renewal',        description: 'Officer at local PDS center demanding ₹1,500 to process ration card renewals.',          type: 'Bribery',       district: 'Karimnagar', scheme: 'PDS',               amount: '₹1,500',  status: 'open',        assignedTo: null,                    remarks: '' },
    { title: 'Mid-day meal funds diverted in 3 schools',      description: 'School principals colluding to show higher attendance. Funds being siphoned.',           type: 'Fund Misuse',   district: 'Hyderabad',  scheme: 'PM Poshan',         amount: '₹6.2L',   status: 'fraud',       assignedTo: byName['Kavita Singh'],  remarks: 'Escalated to district collector.' },
    { title: 'Fake tendering in rural road scheme',           description: "Tender awarded to panchayat president's relative at 2x market rate.",                    type: 'Fake Billing',  district: 'Nizamabad',  scheme: 'PMGSY',             amount: '₹18.5L',  status: 'open',        assignedTo: null,                    remarks: '' },
    { title: 'Irrigation canal repair — bill mismatch',       description: 'Bill showed 400m canal lining but field inspection confirmed only 180m was done.',       type: 'Fake Billing',  district: 'Warangal',   scheme: 'CADA',              amount: '₹4.3L',   status: 'resolved',    assignedTo: byName['Deepa Rao'],     remarks: 'Recovery of ₹3.2L ordered. FIR filed.' },
    { title: 'NREGS worksite attendance manipulation',        description: 'Attendance shows 200+ workers/day; verified headcount shows 60-70.',                     type: 'Ghost Workers', district: 'Karimnagar', scheme: 'MGNREGS',           amount: '₹3.8L',   status: 'in-progress', assignedTo: byName['Meena Iyer'],    remarks: '' },
    { title: 'Health camp supplies not delivered',            description: 'Medical supplies worth ₹9.1L procured on paper but not delivered to PHCs.',             type: 'Fund Misuse',   district: 'Hyderabad',  scheme: 'NRHM',              amount: '₹9.1L',   status: 'open',        assignedTo: null,                    remarks: '' },
    { title: 'Bribery at Jal Jeevan Mission site',            description: 'Engineer demanding ₹25,000 to pass quality inspection for water pipeline.',             type: 'Bribery',       district: 'Nizamabad',  scheme: 'Jal Jeevan Mission',amount: '₹25,000', status: 'in-progress', assignedTo: byName['Suresh Babu'],   remarks: '' },
    { title: 'Duplicate beneficiaries in PM Kisan',           description: '112 beneficiary entries appear to be duplicates or ineligible urban residents.',         type: 'Fund Misuse',   district: 'Warangal',   scheme: 'PM Kisan',          amount: '₹1.2L',   status: 'open',        assignedTo: null,                    remarks: '' },
  ];

  for (const data of complaintData) {
    await new Complaint(data).save();
  }

  console.log('✅ Seed complete!');
  console.log('Admin:  admin@vigilanceiq.gov  /  admin123');
  console.log('Officer: priya@vigilanceiq.gov  /  officer123');
  mongoose.disconnect();
};

seedDB().catch(err => { console.error(err); process.exit(1); });
