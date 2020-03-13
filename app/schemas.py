from app import app, db, ma


from app.models import *


class TaxiRequestSchema(ma.Schema):
    description = ma.String(attribute='comment')
    creator = ma.String(attribute='taxi_creator.full_name')
    approval_data = ma.Nested('TaxiApprovalSchema')
    class Meta:
        include_fk = True
        model = TaxiRequestModel

        fields = ('id', 'creator', 'datenow', 'taxi_company', 'ticket_n', 'dateoftrip',
                    'timeoftrip', 'reason', 'destination', 'expance',
                    'description', 'status', 'email', 'admin_comment', 'approval_data'
                    )


class TaxiApprovalSchema(ma.Schema):
    name = ma.String(attribute='approval_name')
    original = ma.String(attribute='approval_original_name')
    class Meta:
        include_fk = True
        model = TaxiApprovalsModel
        fields = ('id', 'name', 'original')
