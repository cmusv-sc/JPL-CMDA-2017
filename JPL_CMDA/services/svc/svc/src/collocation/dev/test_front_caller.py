
import util as UT

src_data = UT.parse_data_type('/mnt/nas-0-0/users/collocation/ecmwf/idaily-surface')
src_file = '/mnt/nas-0-0/users/collocation/ecmwf/idaily-surface/2008/01/ecmwf-interim-daily-surface-2008-01-06.nc'
src_front_end = UT.get_front_end(src_data, src_file)
#### print 'src_front_end: ', src_front_end

print 'time: ', src_front_end.get_time()
print 'lat: ', src_front_end.get_latitude()
print 'lon: ', src_front_end.get_longitude()
print 'data: ', src_front_end.get_data()
print 'grid info: ', src_front_end.get_src_uniform_grid_info()
