#
# dataset container registry
#
# add new dataset registrations at end of this module
#
from dset_nemo import dset_nemo
from dset_ecmwf_idaily_surface_ncar  import dset_ecmwf_idaily_surface_ncar
from dset_ecmwf_idaily_plevels_ncar  import dset_ecmwf_idaily_plevels_ncar
from dset_ecmwf_yotc_oper_an_ml_ncar import dset_ecmwf_yotc_oper_an_ml_ncar
from dset_ecmwf_yotc_oper_an_pl_ncar import dset_ecmwf_yotc_oper_an_pl_ncar

# the dataset registry itself
reg = {}

# register a dataset container
def register (dset_name, dset_cont, dset_mode):
    # test for name already registered
    if (dset_name in reg.keys()):
        print "error in dataset_registry.register - duplicate name"
        print "dataset name = ", dset_name
    else:
        # register new entry
        reg[dset_name] = dset_cont
        dset_cont.set_name (dset_name)
        dset_cont.set_mode (dset_mode)
# end register

# get a registered dataset container using its name
def get_dataset_container (dset_name):
    # create old style dset container if doesn't exist in reg
    if (dset_name not in reg.keys()):
        print "dataset_registry.get_dset_container - missing registration for ", dset_name
        register (dset_name, dset_nemo(), 0)

    # use adaptor container to convert old front ends to new style
    dset_cont = reg[dset_name]
    print "dataset_registry.get_dataset_container - using ", dset_name

    return dset_cont

# get a list of registered names
def get_dset_names ():
    return reg.keys()

#########################################################
# dataset registrations
register ('ecmwf_idaily_surface_ncar',    dset_ecmwf_idaily_surface_ncar  (), 0) 
register ('ecmwf_idaily_plevels_ncar',    dset_ecmwf_idaily_plevels_ncar  (), 0)

register ('ecmwf_yotc_oper_an_pl_ncar_0', dset_ecmwf_yotc_oper_an_pl_ncar (), 0)
register ('ecmwf_yotc_oper_an_pl_ncar_1', dset_ecmwf_yotc_oper_an_pl_ncar (), 1)
register ('ecmwf_yotc_oper_an_pl_ncar_2', dset_ecmwf_yotc_oper_an_pl_ncar (), 2)
register ('ecmwf_yotc_oper_an_pl_ncar_3', dset_ecmwf_yotc_oper_an_pl_ncar (), 3)

register ('ecmwf_yotc_oper_an_ml_ncar_0', dset_ecmwf_yotc_oper_an_ml_ncar (), 0)
register ('ecmwf_yotc_oper_an_ml_ncar_1', dset_ecmwf_yotc_oper_an_ml_ncar (), 1)
register ('ecmwf_yotc_oper_an_ml_ncar_2', dset_ecmwf_yotc_oper_an_ml_ncar (), 2)
register ('ecmwf_yotc_oper_an_ml_ncar_3', dset_ecmwf_yotc_oper_an_ml_ncar (), 3)

# pre-existing front ends use dset_nemo
register ('cloudsat',       dset_nemo(), 0)
register ('airs',           dset_nemo(), 0)
register ('idaily-surface', dset_nemo(), 0)

# end of dataset registration module

    
