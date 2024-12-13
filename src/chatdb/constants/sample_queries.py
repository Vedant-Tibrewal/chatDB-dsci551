WHERE = [
    "SELECT * FROM hospitals WHERE doctor = 'AprilCox';",
    "SELECT * FROM hospitals WHERE carelevel = 'Emergency';",
    "SELECT * FROM hospitals WHERE roomnumber < 105;",
    "SELECT * FROM hospitals WHERE intakedate >= '01/31/2020';",
    "SELECT * FROM hospitals WHERE dischargedate IS NOT NULL;",
    "SELECT * FROM patients WHERE age > 30;",
    "SELECT * FROM patients WHERE gender = 'Female';",
    "SELECT * FROM patients WHERE bloodtype = 'O+';",
    "SELECT * FROM patients WHERE disease LIKE '%Obes%';",
    "SELECT * FROM patients WHERE patientname IS NOT NULL;",
    "SELECT * FROM insurance WHERE insuranceprovider = 'Aetna';",
    "SELECT * FROM insurance WHERE billingcost > 1000;",
    "SELECT * FROM insurance WHERE patientid IS NOT NULL;",
    "SELECT * FROM insurance WHERE benefit LIKE '%Prem%';",
    "SELECT * FROM insurance WHERE insuranceid IN (SELECT insuranceid FROM insurance WHERE benefit = 'Standard');"
]
JOIN = [
    "SELECT h.*, p.patientname FROM hospitals h JOIN patients p ON h.patientid = p.patientid;",
    "SELECT h.hospitalname, i.insuranceprovider FROM hospitals h JOIN insurance i ON h.insuranceid = i.insuranceid;",
    "SELECT h.hospitalname, p.disease FROM hospitals h JOIN patients p ON h.patientid = p.patientid WHERE h.roomnumber = 202;",
    "SELECT h.hospitalname, COUNT(p.patientid) FROM hospitals h JOIN patients p ON h.patientid = p.patientid GROUP BY h.hospitalname;",
    "SELECT p.*, h.hospitalname FROM patients p JOIN hospitals h ON p.patientid = h.patientid;",
    "SELECT p.patientname, i.insuranceprovider FROM patients p JOIN insurance i ON p.patientid = i.patientid;",
    "SELECT p.patientname, p.age, COUNT(DISTINCT h.admissionid) FROM patients p JOIN hospitals h ON p.patientid = h.patientid GROUP BY p.patientname;",
    "SELECT p.age, AVG(i.billingcost) FROM patients p JOIN insurance i ON p.patientid = i.patientid GROUP BY p.age;",
    "SELECT i.*, p.patientname FROM insurance i JOIN patients p ON i.patientid = p.patientid;",
    "SELECT i.insuranceprovider, h.hospitalname FROM insurance i JOIN hospitals h ON i.patientid = h.patientid;",
    "SELECT i.insuranceprovider, COUNT(p.patientid) FROM insurance i JOIN patients p ON i.patientid = p.patientid GROUP BY i.insuranceprovider;",
    "SELECT i.insuranceid, p.patientname FROM insurance i JOIN patients p ON i.patientid = p.patientid WHERE i.billingcost < 500;"
]
GROUP_BY = [
    "SELECT hospitalname, COUNT(*) AS total_patients FROM hospitals GROUP BY hospitalname;",
    "SELECT doctor, COUNT(*) FROM hospitals GROUP BY doctor HAVING COUNT(*) > 1;",
    "SELECT carelevel, AVG(roomnumber) FROM hospitals GROUP BY carelevel;",
    "SELECT intakedate, COUNT(*) FROM hospitals GROUP BY intakedate ORDER BY COUNT(*) DESC;",
    "SELECT roomnumber, MAX(carelevel) FROM hospitals GROUP BY roomnumber;",
    "SELECT gender, COUNT(*) AS total_patients FROM patients GROUP BY gender;",
    "SELECT bloodtype, COUNT(*) FROM patients GROUP BY bloodtype HAVING COUNT(*) > 5;",
    "SELECT disease, COUNT(*) FROM patients GROUP BY disease ORDER BY COUNT(*) DESC;",
    "SELECT age, AVG(age) FROM patients GROUP BY age;",
    "SELECT insuranceprovider, COUNT(*) AS total_patients FROM insurance GROUP BY insuranceprovider;",
    "SELECT billingcost, COUNT(*) FROM insurance GROUP BY billingcost HAVING COUNT(*) > 5;",
    "SELECT patientid, AVG(billingcost) FROM insurance GROUP BY patientid;",
    "SELECT benefit, SUM(billingcost) FROM insurance GROUP BY benefit;",
    "SELECT COUNT(*) AS total_records FROM insurance;"
]
ORDER_BY = [
    "SELECT * FROM hospitals ORDER BY intakedate DESC;",
    "SELECT * FROM hospitals ORDER BY roomnumber ASC;",
    "SELECT * FROM hospitals ORDER BY doctor;",
    "SELECT * FROM hospitals ORDER BY carelevel DESC, roomnumber ASC;",
    "SELECT * FROM hospitals ORDER BY admissionid;",
    "SELECT * FROM patients ORDER BY patientname ASC;",
    "SELECT * FROM patients ORDER BY age DESC;",
    "SELECT * FROM patients ORDER BY disease;",
    "SELECT * FROM patients ORDER BY bloodtype, patientname;",
    "SELECT * FROM patients ORDER BY patientid DESC;",
    "SELECT * FROM insurance ORDER BY billingcost DESC;",
    "SELECT * FROM insurance ORDER BY insuranceprovider;",
    "SELECT * FROM insurance ORDER BY patientid ASC;",
    "SELECT * FROM insurance ORDER BY benefit, insuranceprovider DESC;",
    "SELECT * FROM insurance ORDER BY insuranceid DESC;"
]
LIMIT = [
    "SELECT * FROM hospitals LIMIT 5;",
    "SELECT * FROM hospitals ORDER BY intakedate LIMIT 10;",
    "SELECT * FROM hospitals WHERE carelevel = 'Emergency' LIMIT 3;",
    "SELECT * FROM hospitals ORDER BY dischargedate DESC LIMIT 1;",
    "SELECT * FROM hospitals LIMIT 100;",
    "SELECT * FROM patients LIMIT 5;",
    "SELECT * FROM patients ORDER BY age LIMIT 10;",
    "SELECT * FROM patients LIMIT 3;",
    "SELECT * FROM patients ORDER BY patientid DESC LIMIT 1;",
    "SELECT * FROM patients LIMIT 50;",
    "SELECT * FROM insurance LIMIT 5;",
    "SELECT * FROM insurance ORDER BY billingcost LIMIT 10;",
    "SELECT * FROM insurance LIMIT 3;",
    "SELECT * FROM insurance ORDER BY patientid DESC LIMIT 1;",
    "SELECT * FROM insurance LIMIT 50;"
]

# MONGODB
FILTER = [
    "db.hospitals.find({'doctor': 'AprilCox'})",
    "db.hospitals.find({'carelevel': 'Emergency'})",
    "db.hospitals.find({'roomnumber': {'$lt': 105}})",
    "db.hospitals.find({'intakedate': {'$gte': datetime.datetime(2020, 1, 31, 0, 0)}})",
    "db.hospitals.find({'dischargedate': {'$ne': None}})",
    "db.patients.find({'age': {'$gt': 30}})",
    "db.patients.find({'gender': 'Female'})",
    "db.patients.find({'bloodtype': 'O+'})",
    "db.patients.find({'disease': {'$regex': 'Obes'}})",
    "db.patients.find({'patientname': {'$ne': None}})",
    "db.insurance.find({'insuranceprovider': 'Aetna'})",
    "db.insurance.find({'billingcost': {'$gt': 1000}})",
    "db.insurance.find({'patientid': {'$ne': None}})",
    "db.insurance.find({'benefit': {'$regex': 'Prem'}})"
]

# LOOKUP = [
#     """db.hospitals.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient'
#         }},
#         {'$unwind': '$patient'},
#         {'$project': {
#             'hospitalname': 1,
#             'patientname': '$patient.patientname'
#         }}
#     ])""",
#     """db.hospitals.aggregate([
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'insuranceid',
#             'foreignField': 'insuranceid',
#             'as': 'insurance'
#         }},
#         {'$unwind': '$insurance'},
#         {'$project': {
#             'hospitalname': 1,
#             'insuranceprovider': '$insurance.insuranceprovider'
#         }}
#     ])""",
#     """db.hospitals.aggregate([
#         {'$match': {'roomnumber': 202}},
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient'
#         }},
#         {'$unwind': '$patient'},
#         {'$project': {
#             'hospitalname': 1,
#             'disease': '$patient.disease'
#         }}
#     ])""",
#     """db.hospitals.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patients'
#         }},
#         {'$group': {
#             '_id': '$hospitalname',
#             'patientCount': {'$sum': {'$size': '$patients'}}
#         }}
#     ])""",
#     """db.patients.aggregate([
#         {'$lookup': {
#             'from': 'hospitals',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'hospital'
#         }},
#         {'$unwind': '$hospital'},
#         {'$project': {
#             'patitentname': 1,
#             'hospitalname': '$hospital.hospitalname'
#         }}
#     ])""",
#     """db.patients.aggregate([
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'insurance'
#         }},
#         {'$unwind': '$insurance'},
#         {'$project': {
#             'patientname': 1,
#             'insuranceprovider': '$insurance.insuranceprovider'
#         }}
#     ])""",
#     """db.patients.aggregate([
#         {'$lookup': {
#             'from': 'hospitals',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'hospitals'
#         }},
#         {'$project': {
#             'patientname': 1,
#             'age': 1,
#             'uniqueAdmissions': {'$size': {'$setUnion': '$hospitals.admissionid'}}
#         }}
#     ])""",
#     """db.patients.aggregate([
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'insurance'
#         }},
#         {'$unwind': '$insurance'},
#         {'$group': {
#             '_id': '$age',
#             'avgBillingCost': {'$avg': '$insurance.billingcost'}
#         }}
#     ])""",
#     """db.insurance.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient'
#         }},
#         {'$unwind': '$patient'},
#         {'$project': {
#             'insuranceprovider': 1,
#             'patientname': '$patient.patientname'
#         }}
#     ])""",
#     """db.insurance.aggregate([
#         {'$lookup': {
#             'from': 'hospitals',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'hospital'
#         }},
#         {'$unwind': '$hospital'},
#         {'$project': {
#             'insuranceprovider': 1,
#             'hospitalname': '$hospital.hospitalname'
#         }}
#     ])""",
#     """db.insurance.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patients'
#         }},
#         {'$group': {
#             '_id': '$insuranceprovider',
#             'patientCount': {'$sum': {'$size': '$patients'}}
#         }}
#     ])""",
#     """db.insurance.aggregate([
#         {'$match': {'billingcost': {'$lt': 500}}},
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient'
#         }},
#         {'$unwind': '$patient'},
#         {'$project': {
#             'insuranceid': 1,
#             'patientname': '$patient.patientname'
#         }}
#     ])"""
# ]

# LOOKUP = [
#     """db.patients.aggregate([
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'insurance_details'
#         }}
#     ])""",

#     """db.insurance.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient_details'
#         }}
#     ])""",

#     """db.hospitals.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient_details'
#         }},
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'insuranceid',
#             'foreignField': 'insuranceid',
#             'as': 'insurance_details'
#         }}
#     ])""",

#     """db.patients.aggregate([
#         {'$match': {
#             'disease': 'Hypertension'
#         }},
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'insurance_details'
#         }}
#     ])""",

#     """db.patients.aggregate([
#         {'$match': {
#             'age': 30
#         }},
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'insurance_details'
#         }},
#         {'$project': {
#             'insuranceprovider': '$insurance_details.insuranceprovider'
#         }}
#     ])""",

#     """db.hospitals.aggregate([
#         {'$match': {
#             'doctor': 'Dr. Smith'
#         }},
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient_details'
#         }}
#     ])""",

#     """db.hospitals.aggregate([
#         {'$match': {
#             'carelevel': 'Emergency'
#         }},
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient_details'
#         }}
#     ])""",

#     """db.hospitals.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient_details'
#         }},
#         {'$project': {
#             'patient_details': 1,
#             'testresults': 1
#         }}
#     ])""",

#     """db.patients.aggregate([
#         {'$match': {
#             'bloodtype': 'O+'
#         }},
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'insurance_details'
#         }}
#     ])""",

#     """db.insurance.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient_details'
#         }},
#         {'$match': {
#             'patient_details.disease': 'Hypertension'
#         }}
#     ])""",

#     """db.hospitals.aggregate([
#         {'$lookup': {
#             'from': 'patients',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'patient_details'
#         }},
#         {'$lookup': {
#             'from': 'insurance',
#             'localField': 'insuranceid',
#             'foreignField': 'insuranceid',
#             'as': 'insurance_details'
#         }},
#         {'$project': {
#             'patient_details.patientname': 1,
#             'insurance_details.insuranceprovider': 1
#         }}
#     ])""",

#     """db.patients.aggregate([
#         {'$lookup': {
#             'from': 'hospitals',
#             'localField': 'patientid',
#             'foreignField': 'patientid',
#             'as': 'hospital_admissions'
#         }}
#     ])"""
# ]


GROUP = [
    "db.hospitals.aggregate([{'$group': {'_id': '$hospitalname', 'total_patients': {'$sum': 1}}}])",
    "db.hospitals.aggregate([{'$group': {'_id': '$doctor', 'count': {'$sum': 1}}}, {'$match': {'count': {'$gt': 1}}}])",
    "db.hospitals.aggregate([{'$group': {'_id': '$carelevel', 'avg_roomnumber': {'$avg': '$roomnumber'}}}])",
    "db.hospitals.aggregate([{'$group': {'_id': '$intakedate', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}])",
    "db.hospitals.aggregate([{'$group': {'_id': '$roomnumber', 'max_carelevel': {'$max': '$carelevel'}}}])",
    "db.patients.aggregate([{'$group': {'_id': '$gender', 'total_patients': {'$sum': 1}}}])",
    "db.patients.aggregate([{'$group': {'_id': '$bloodtype', 'count': {'$sum': 1}}}, {'$match': {'count': {'$gt': 5}}}])",
    "db.patients.aggregate([{'$group': {'_id': '$disease', 'count': {'$sum': 1}}}, {'$sort': {'count': -1}}])",
    "db.patients.aggregate([{'$group': {'_id': '$age', 'avg_age': {'$avg': '$age'}}}])",
    "db.insurance.aggregate([{'$group': {'_id': '$insuranceprovider', 'total_patients': {'$sum': 1}}}])",
    "db.insurance.aggregate([{'$group': {'_id': '$billingcost', 'count': {'$sum': 1}}}, {'$match': {'count': {'$gt': 5}}}])",
    "db.insurance.aggregate([{'$group': {'_id': '$patientid', 'avg_billingcost': {'$avg': '$billingcost'}}}])",
    "db.insurance.aggregate([{'$group': {'_id': '$benefit', 'total_billingcost': {'$sum': '$billingcost'}}}])",
    "db.insurance.aggregate([{'$group': {'_id': null, 'total_records': {'$sum': 1}}}])"
]

SORT = [
    "db.hospitals.find({}).sort({'intakedate': -1})",
    "db.hospitals.find({}).sort({'roomnumber': 1})",
    "db.hospitals.find({}).sort({'doctor': 1})",
    "db.hospitals.find({}).sort({'carelevel': -1, 'roomnumber': 1})",
    "db.hospitals.find({}).sort({'admissionid': 1})",
    "db.patients.find({}).sort({'patientname': 1})",
    "db.patients.find({}).sort({'age': -1})",
    "db.patients.find({}).sort({'disease': 1})",
    "db.patients.find({}).sort({'bloodtype': 1, 'patientname': 1})",
    "db.patients.find({}).sort({'patientid': -1})",
    "db.insurance.find({}).sort({'billingcost': -1})",
    "db.insurance.find({}).sort({'insuranceprovider': 1})",
    "db.insurance.find({}).sort({'patientid': 1})",
    "db.insurance.find({}).sort({'benefit': 1, 'insuranceprovider': -1})",
    "db.insurance.find({}).sort({'insuranceid': -1})"
]

MONGO_LIMIT = [
    "db.hospitals.find({}).limit(5)",
    "db.hospitals.find({}).sort({'intakedate': 1}).limit(10)",
    "db.hospitals.find({'carelevel': 'Emergency'}).limit(3)",
    "db.hospitals.find({}).sort({'dischargedate': -1}).limit(1)",
    "db.hospitals.find({}).limit(100)",
    "db.patients.find({}).limit(5)",
    "db.patients.find({}).sort({'age': 1}).limit(10)",
    "db.patients.find({}).limit(3)",
    "db.patients.find({}).sort({'patientid': -1}).limit(1)",
    "db.patients.find({}).limit(50)",
    "db.insurance.find({}).limit(5)",
    "db.insurance.find({}).sort({'billingcost': 1}).limit(10)",
    "db.insurance.find({}).limit(3)",
    "db.insurance.find({}).sort({'patientid': -1}).limit(1)",
    "db.insurance.find({}).limit(50)"
]
