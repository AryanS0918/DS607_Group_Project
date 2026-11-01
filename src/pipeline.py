from .data_loader import prepare_returns
from .eda_and_intervals import step4,step5,step6
from .distribution_fitting import step7,step8
from .dependence_and_tests import step9,step10,step11

def run_all():
    prepare_returns(); step4(); step5(); step6(); step7(); step8(); step9(); step10(); step11()
if __name__=='__main__': run_all()
