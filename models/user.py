from models.database import DataAccess
from werkzeug.security import check_password_hash, generate_password_hash


class User:
    def __init__(self, username, name, role, designation, password="", status="Active", dept="Medical",
                 ward=None, team=None, password_hash="", revision=""):
        self.database = DataAccess("users").db
        self.username = username
        self.name = name
        self.role = role
        self.designation = designation
        self.password = password
        self.status = status
        self.ward = ward
        self.department = dept
        self.team = team
        self.rev = revision
        self.password_hash = password_hash

    @staticmethod
    def get(username):
        user = DataAccess("users").db.get(username)
        if user is not None:
            user = User(user.get('_id'), user.get('name', "Unknown"), user.get('role'),
                        user.get('designation', 'Unassigned'), "", user.get('status', "Active"),
                        user.get('department', "Medical"), user.get('ward', ""), user.get('team', "Unassigned"),
                        user.get("password_hash"), user.get("_rev"))
        return user

    @staticmethod
    def get_team_members(team):
        users = []
        user_results = DataAccess("users").db.find({"selector": {"team": team}, "fields": ["_id"], "limit": 5000})
        for provider in user_results:
            users.append(provider["_id"])
        return users

    @staticmethod
    def all():
        return DataAccess("users").db.find({"selector": {"_id": {"$gt": None}}, "limit": 2000})
        
    @staticmethod
    def get_active_prescribers():
        return DataAccess("users").db.find({"selector": {"role": "Doctor", "status": "Active"}, "limit": 5000})

    def save(self):
        user = self.__repr__()
        if self.rev == "":
            user.pop("_rev")
        if not self.password == "":
            user["password_hash"] = generate_password_hash(self.password)
        elif not self.password_hash == "":
            user["password_hash"] = self.password_hash
        self.database.save(user)

    def is_active(self):
        return False if self.status == "Inactive" else True

    def __str__(self):
        return 'User(username: ' + self.username + ', name: ' + self.name + ', role: ' + self.role + ', designation: ' + self.designation + ', status: ' + self.status + ', department: ' + self.department + ', ward: ' + self.ward + ')'

    def __repr__(self):
        return {"_id": self.username, "name": self.name, "role": self.role, 'designation': self.designation,
                'status': self.status, 'department': self.department, 'team': self.team, 'ward': self.ward,
                'type': "user", "_rev": self.rev}
