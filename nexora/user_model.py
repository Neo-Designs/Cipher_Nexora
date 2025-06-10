class User:
    def __init__(self, user_row):
        self.id = user_row.UserID
        self.email = user_row.Email
        self.role = user_row.Role
        self.full_name = user_row.FullName
