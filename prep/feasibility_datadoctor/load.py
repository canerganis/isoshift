import json,os,sys
from matminer.datasets import load_dataset
meta=json.load(open(os.path.join(os.path.dirname(__import__('matminer').__file__),'datasets','dataset_metadata.json')))
names=['expt_gap','expt_gap_kingsbury','matbench_expt_gap','expt_formation_enthalpy','expt_formation_enthalpy_kingsbury','matbench_expt_is_metal','glass_binary','glass_ternary_landolt','citrine_thermal_conductivity','ucsb_thermoelectrics','steel_strength','superconductivity2018','heusler_magnetic','brgoch_superhard_training','double_perovskites_gap','wolverton_oxides','flla']
for n in names:
    try:
        d=load_dataset(n)
        print('==',n,d.shape,list(d.columns)[:15])
        print('  ref in meta:',meta[n].get('reference','')[:200].replace('\n',' '))
        print(d.head(2).to_string()[:600])
        d.to_pickle(f'{os.environ["MATMINER_DATA"]}/{n}.pkl')
    except Exception as e: print('ERR',n,e)
