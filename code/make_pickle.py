# Dvirs Sadon
import cPickle as pickle
import os


class Pickfile:
    """A class for pickle file type"""
    def __init__(self, name):
        self.name = name

    def create_file(self, value):
        """Gets a value and creates a picle file with that value by the name of the given object"""
        if not os.path.exists(self.name):
            users = value  # List of all users registered (Non workers)
            # print users
            with open(self.name, 'wb') as handle:
                pickle.dump(users, handle, protocol=pickle.HIGHEST_PROTOCOL)
                return handle
        else:
            with open(self.name, 'rb') as pick:
                users = pickle.load(pick)
                return users

    def get_value(self):
        """Returns the value inside the pickle file"""
        with open(self.name, "rb") as handle:
            myvalue = pickle.load(handle)
            return myvalue

    def update_file(self, data):
        """Gets a value and updates the value inside the file"""
        with open(self.name, 'wb') as handle:
            pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def open_file(self, typee):
        """Gets a type(rb,wb...) opens the file and returns the open file"""
        return open(self.name, typee)
