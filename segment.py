import sys
import PIL
import ipdb

import numpy as np
import mahotas
import pylab
from scipy.cluster.vq import kmeans,vq
from scipy import ndimage


R, G, B = range(3)

def main(infile):
    k = 3
    img = mahotas.imread(infile)
    blue_component = img[:,:,B]
    f = ndimage.gaussian_filter(blue_component, 12)
    #f = mahotas.gaussian_filter(blue_component, 12)
    #f = f > f.mean()
    p = f.flatten()
    centroids, _ = kmeans(p,k)
    centroids.sort()
    clustered, _ = vq(p, centroids)
    clustered[clustered == k-1] = 0
    print np.unique(clustered)
    mask = clustered.reshape(f.shape)

    masked = blue_component * mask

    mahotas.imsave('mask%s.jpg' % k, mask)
    mahotas.imsave('masked%s.jpg' % k, masked)
    #save_imarray(f, 'out.jpg')

def save_imarray(imarray, outfile):
    PIL.Image.fromarray(imarray).save(outfile)

if __name__ == '__main__':
    try:
        assert len(sys.argv) == 2
        infile = sys.argv[1]
    except Exception:
        print 'Usage %s <infile>' % __file__
    else:
        main(infile)
