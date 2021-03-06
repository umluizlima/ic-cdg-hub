from app.models import db
import app.models.utils as utils


definition = {
    'types': {
        'name': [str],
        'description': [str, type(None)],
        'date_start': [str],
        'date_end': [str],
        'user_id': [int, type(None)],
        'thirdparty_id': [int, type(None)]
    },
    'required': ['name', 'date_start', 'date_end'],
    'unique': []
}


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    date_start = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey('user.id',
                                      onupdate='CASCADE',
                                      ondelete='SET NULL'),
                        nullable=True)
    thirdparty_id = db.Column(db.Integer,
                              db.ForeignKey('thirdparty.id',
                                            onupdate='CASCADE',
                                            ondelete='SET NULL'),
                              nullable=True)

    def to_dict(self):
        obj = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date_start": self.date_start.isoformat(timespec='minutes'),
            "date_end": self.date_end.isoformat(timespec='minutes'),
            "user_id": self.user_id,
            "thirdparty_id": self.thirdparty_id
        }
        print(type(self.date_start))
        return obj

    def from_dict(self, data):
        for field in ['name', 'description', 'date_start', 'date_end',
                      'user_id', 'thirdparty_id']:
            if field in data:
                setattr(self, field, data[field])

    @staticmethod
    def check_data(data: dict, new: bool = False):
        error = utils.check_data(data, definition, new) \
            or utils.check_datetime(data, 'date_start') \
            or utils.check_datetime(data, 'date_end')
        if 'date_start' in data \
                and 'date_end' in data \
                and data['date_end'] <= data['date_start']:
            error = 'date_start deve ser menor que date_end'
        return error
