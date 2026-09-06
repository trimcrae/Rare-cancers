"""Synthetic test of fixed triage comparisons and denominator safety."""
import copy,json,pathlib
import summarize
HERE=pathlib.Path(__file__).resolve().parent
def case(name,z,other,truth):
    d={'case_id':name,'source_group':name,'curve':{'curve_id':name},'seed':61001,'precision':2,'density':'sparse','status':'returned','original':{'reject':truth,'evaluable':True},'methods':{}}
    for method,score in zip(summarize.METHODS,(z,other)):
        reject=abs(score)>summarize.CRIT
        d['methods'][method]={'status':'success','statistic':{'z':score,'reject':reject},'threshold_error':reject!=truth,'flip_direction':('false_reject' if reject else 'false_nonreject') if reject!=truth else None,'sign_flip':False}
    return d
def main():
    cases=[case('c1',3.,0.,False),case('c2',2.8,2.8,True),case('c3',.2,.2,False),case('c4',1.9,1.9,False)]
    before=copy.deepcopy(cases)
    base=summarize.selected(cases,'IPDfromKM','margin',.5)
    augmented=summarize.selected(cases,'IPDfromKM','margin_minus_disagreement',.5)
    assert [c['case_id'] for c in base]==['c3','c1']
    assert [c['case_id'] for c in augmented]==['c3','c2']
    assert summarize.assessment(base,'IPDfromKM')['errors']==1
    assert summarize.assessment(augmented,'IPDfromKM')['errors']==0
    result=summarize.summarize(cases);assert cases==before
    assert result['always_nonsignificant']=={'errors':1,'retained':4}
    cases.append({'case_id':'unrun','source_group':'held','curve':{'curve_id':'none'},'seed':61001,'precision':2,'density':'sparse','status':'unrun_after_discrepancy','original':None})
    failed=summarize.summarize(cases)
    assert failed['attempted_cases']==5 and failed['dual_success_fraction']==.8
    assert not failed['continuation_checks']['complete_planned_execution']
    assert not failed['continue_to_held_out']
    receipt={'passed':True,'checks':['exact matched retention','fixed prediction invariance','hand-computed error comparison','always-nonsignificant baseline','unrun complete-denominator safety']}
    (HERE/'summary-fixture-verification.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
if __name__=='__main__':main()
