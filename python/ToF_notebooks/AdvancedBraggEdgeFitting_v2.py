import numpy as np
from numpy import pi, r_, math, random
import matplotlib.pyplot as plt
from scipy import optimize
from scipy.optimize import curve_fit
from scipy.special import erfc
from lmfit import Model
from numpy import loadtxt
from scipy.signal import argrelextrema
from TOF_routines import find_nearest
from TOF_routines import find_first
from TOF_routines import find_last

# def term0(t,a2,a6):
#     return  a2 * (t - a6)

# def term1(t,a2,a5,a6):
#     return ((a5 - a2) / 2) * (t - a6)

def term3(t,t0,sigma):
    return erfc(-((t-t0)/(sigma * math.sqrt(2))))

def term4(t,t0,alpha,sigma):
    return np.exp(-((t-t0)/alpha) + ((sigma*sigma)/(2*alpha*alpha)))

def term5(t,t0,alpha,sigma):
    return erfc(-((t-t0)/(sigma * math.sqrt(2))) + sigma/alpha)

def line_after(t,a1,a2):
    return a1+a2*t

def line_before(t,a5,a6):
    return a5+a6*t

def exp_after(t,a1,a2):
    return np.exp(-(a1+a2*t))

def exp_before(t,a5,a6):
    return np.exp(-(a5+a6*t))

def exp_combined(t,a1,a2,a5,a6):
    return exp_after(t,a1,a2)*exp_before(t,a5,a6)

def B(t,t0,alpha,sigma):
    return (0.5*(term3(t,t0,sigma) - term4(t,t0,alpha,sigma)* term5(t,t0,alpha,sigma)))

def BraggEdgeLinear(t,t0,alpha,sigma,a1,a2,a5,a6):
    return line_after(t,a1,a2)*B(t,t0,alpha,sigma)+line_before(t,a5,a6)*(1-B(t,t0,alpha,sigma))

def BraggEdgeExponential(t,t0,alpha,sigma,a1,a2,a5,a6):
    return exp_after(t,a1,a2) * ( exp_before(t,a5,a6)+ (1-exp_before(t,a5,a6)) * B(t,t0,alpha,sigma) )
    

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)



# def AdvancedBraggEdegFittingAll(t,t0,sigma,alpha,a1,a2,a5,a6):
#     return a1 + term0(t,a2,a6) + term1(t,a2,a5,a6) * (1-(term3(t,t0,sigma) - term4(t,t0,alpha,sigma)* term5(t,t0,alpha,sigma)))

def AdvancedBraggEdgeFitting(myspectrum, myrange, myTOF, est_pos, est_sigma, est_alpha, bool_print, bool_average, bool_linear): ## my range should be now the index position of the spectra that I want to study, est_pos is also the index position where the expected peak is 
    
    #get the part of the spectrum that I want to fit
#    mybragg = -1*np.log(myspectrum[myrange[0]:myrange[1]]/np.max(myspectrum[myrange[0]:myrange[1]]))
#    mybragg = mybragg/np.max(mybragg)# iniziamo senza rumore aggiunto
    mybragg= myspectrum[myrange[0]:myrange[1]]

    
    if (bool_average):
        mybragg = running_mean(mybragg,3)
    
    #first step: estimate the linear function before and after the Bragg Edge
    
#     est_pos=est_pos-myrange[0]
#     t=np.linspace(0,np.size(mybragg)-1,np.size(mybragg))
#     t_before= t[0:est_pos-int(est_pos*0.3)]
#     bragg_before=mybragg[0:est_pos-int(est_pos*0.3)]
#     t_after= t[est_pos+int(est_pos*0.2):-1]
#     bragg_after=mybragg[est_pos+int(est_pos*0.2):-1]
 
    # here I try to fit in TOF and not in unitless units. This should give me more meaningfull results in the paramters I believe

    t = myTOF[myrange[0]:myrange[1]]
    est_pos=est_pos-myrange[0] # I move the estimated position relative to the studied range, this is an index 
    t0_f=myTOF[est_pos+myrange[0]] # this is the actual estimated first position in TOF [s]
    
    plt.figure()
    plt.plot(t, mybragg)
    plt.plot(t0_f, mybragg[est_pos],'x', markeredgewidth=3, c='orange')
    
    t_before= t[0:est_pos-int(est_pos*0.3)]
    bragg_before=mybragg[0:est_pos-int(est_pos*0.3)]
#     t_after= t[est_pos+int(est_pos*0.2):-1]
#     bragg_after=mybragg[est_pos+int(est_pos*0.2):-1]
    t_after= t[est_pos:-1]
    bragg_after=mybragg[est_pos:-1]
    


    
    
    if (bool_linear):    
        [slope_before, interception_before] = np.polyfit(t_before, bragg_before, 1)
        [slope_after, interception_after] = np.polyfit(t_after, bragg_after, 1)
        #first guess of paramters
        a2_f=slope_after
        a5_f=interception_before
        a6_f=slope_before
        a1_f=interception_after
        plt.figure()
        plt.plot(t_before,bragg_before,'.g')
        plt.plot(t_after,bragg_after,'.r')
        plt.plot(t,mybragg)  
        plt.plot(t,interception_before+slope_before*t,'g')
        plt.plot(t,interception_after+slope_after*t,'r')
        plt.title('linear fitting before and after the given edge position')
        gmodel = Model(BraggEdgeLinear)
    else:
        [slope_before, interception_before] = np.polyfit(t_before, bragg_before, 1)
        [slope_after, interception_after] = np.polyfit(t_after, bragg_after, 1)
        #first guess of paramters
        a2_f=slope_after
        a5_f=interception_before
        a6_f=slope_before
        a1_f=interception_after
        
        exp_model_after = Model(exp_after)
        params = exp_model_after.make_params(a1=a1_f, a2=a2_f)
        result_exp_model_after = exp_model_after.fit(bragg_after,params,t=t_after)
        a1_f=result_exp_model_after.best_values.get('a1')
        a2_f=result_exp_model_after.best_values.get('a2')
        
        exp_model_before = Model(exp_combined)
        params = exp_model_before.make_params(a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f)
        params['a1'].vary = False
        params['a2'].vary = False
        result_exp_model_before = exp_model_before.fit(bragg_before,params,t=t_before)
        a5_f=result_exp_model_before.best_values.get('a5')
        a6_f=result_exp_model_before.best_values.get('a6')
        gmodel = Model(BraggEdgeExponential)
        plt.figure()
        plt.plot(t_before,bragg_before,'.r')
        plt.plot(t_after,bragg_after,'.g')
        plt.plot(t,mybragg)

        plt.plot(t,interception_before+slope_before*t,'--r')
        plt.plot(t,interception_after+slope_after*t,'--g')
        plt.plot(t,exp_after(t,a1_f,a2_f),'g')
        plt.plot(t,exp_combined(t,a1_f,a2_f,a5_f,a6_f),'r')
        plt.title('eponential fitting before and after the given edge position')
#         plt.plot(t, BraggEdgeExponential(t,t0_f,est_alpha,est_sigma,a1_f,a2_f,a5_f,a6_f))
            
    

    
    sigma_f = est_sigma
    alpha_f = est_alpha
    # method='trust_exact'
    # method='nelder' #not bad
    # method='differential_evolution' # needs bounds
    # method='basinhopping' # not bad
    # method='lmsquare' # this should implement the Levemberq-Marquardt but it says Nelder-Mead method (which should be Amoeba)
    method ='least_squares' # default and it implements the Levenberg-Marquardt
    

#     gmodel = Model(BraggEdgeLinear)
    
    params = gmodel.make_params(t0=t0_f,sigma=sigma_f, alpha=alpha_f, a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f)
    
    first_guess = gmodel.eval(params, t=t)
    plt.figure()
    plt.plot(t,first_guess,'b')
    plt.plot(t,mybragg,'b--')
    plt.title('initial BE with given parameters')
    params['alpha'].vary = False
    params['sigma'].vary = False
    params['t0'].vary = False
    params['a2'].vary= False
    params['a5'].vary = False
    
    
    result1 = gmodel.fit(mybragg, params, t=t, method=method, nan_policy='propagate')
#    print(result1.fit_report())
    
#    plt.figure
#    plt.plot(t, mybragg, 'b-')
#    plt.plot(t, result1.init_fit, 'k--')
#    plt.plot(t, result1.best_fit, 'r-')
#    plt.show()
    
    a1_f=result1.best_values.get('a1')
    a6_f=result1.best_values.get('a6')
    
    params = gmodel.make_params(t0=t0_f,sigma=sigma_f, alpha=alpha_f, a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f)
    params['alpha'].vary = False
    params['sigma'].vary = False
    params['t0'].vary = False
    params['a1'].vary= False
    params['a6'].vary = False
        

    result2 = gmodel.fit(mybragg, params, t=t, method=method, nan_policy='propagate')
#    print(result2.fit_report())
#    plt.figure
#    plt.plot(t, mybragg, 'b-')
#    plt.plot(t, result2.init_fit, 'k--')
#    plt.plot(t, result2.best_fit, 'r-')
#    plt.show()

    a2_f = result2.best_values.get('a2')
    a5_f = result2.best_values.get('a5')
    
    params = gmodel.make_params(t0=t0_f,sigma=sigma_f, alpha=alpha_f, a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f)
    params['a2'].vary = False
    params['a5'].vary = False
    params['a1'].vary= False
    params['a6'].vary = False
    params['sigma'].vary= False
    params['alpha'].vary = False


    result3=gmodel.fit(mybragg, params, t=t, method=method, nan_policy='propagate')
#    print(result3.fit_report())
#    plt.figure
#    plt.plot(t, mybragg, 'b-')
#    plt.plot(t, result3.init_fit, 'k--')
#    plt.plot(t, result3.best_fit, 'r-')
#    plt.show()
    
    t0_f=result3.best_values.get('t0')
#     sigma_f=result3.best_values.get('sigma')
#     alpha_f=result3.best_values.get('alpha')

    params = gmodel.make_params(t0=t0_f,sigma=sigma_f, alpha=alpha_f, a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f)
    params['a2'].vary = False
    params['a5'].vary = False
    params['a1'].vary= False
    params['a6'].vary = False
#     params['t0'].vary= False

    result4=gmodel.fit(mybragg, params, t=t, nan_policy='propagate',method=method)
                       


#    print(result4.fit_report())
#    plt.figure
#    plt.plot(t, mybragg, 'b-')
#    plt.plot(t, result4.init_fit, 'k--')
#    plt.plot(t, result4.best_fit, 'r-')
#    plt.show()
    
    sigma_f=result4.best_values.get('sigma')
    alpha_f=result4.best_values.get('alpha')
    t0_f=result4.best_values.get('t0')
    
    
    params = gmodel.make_params(t0=t0_f,sigma=sigma_f, alpha=alpha_f, a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f)
    params['t0'].vary = False
    params['sigma'].vary = False
    params['alpha'].vary= False
    
    
    result5 = gmodel.fit(mybragg, params, t=t, nan_policy='propagate', method=method)
#    print(result5.fit_report())
#    plt.figure
#    plt.plot(t, mybragg, 'b-')
#    plt.plot(t, result5.init_fit, 'k--')
#    plt.plot(t, result5.best_fit, 'r-')
#    plt.show()
    
    a1_f =result5.best_values.get('a1')
    a2_f = result5.best_values.get('a2')
    a5_f = result5.best_values.get('a5')
    a6_f = result5.best_values.get('a6')
#     t0_f=result5.best_values.get('t0')
#     sigma_f=result5.best_values.get('sigma')
#     alpha_f=result5.best_values.get('alpha')

    params = gmodel.make_params(t0=t0_f,sigma=sigma_f, alpha=alpha_f, a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f)
    params['a2'].vary = False
    params['a5'].vary = False
    params['a1'].vary= False
    params['a6'].vary = False
    
    result6= gmodel.fit(mybragg, params, t=t, nan_policy='propagate', method=method)



#     result6=gmodel6.fit(mybragg,t=t, t0=t0_f,sigma=sigma_f, alpha=alpha_f, a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f, nan_policy='propagate', method=method)
    
#    print(result6.fit_report())
#    plt.figure
#    plt.plot(t, mybragg, 'b-')
#    plt.plot(t, result6.init_fit, 'k--')
#    plt.plot(t, result6.best_fit, 'r-')
#    plt.show()

    t0_f=result6.best_values.get('t0')
    sigma_f=result6.best_values.get('sigma')
    alpha_f=result6.best_values.get('alpha')

    params = gmodel.make_params(t0=t0_f,sigma=sigma_f, alpha=alpha_f, a1=a1_f, a2=a2_f, a5=a5_f, a6=a6_f)

    result7 = gmodel.fit(mybragg, params, t=t, nan_policy='propagate', method=method)
    
    print(result7.fit_report())

    
    t0_f=result7.best_values.get('t0')
    sigma_f=result7.best_values.get('sigma')
    alpha_f=result7.best_values.get('alpha')
    a1_f =result7.best_values.get('a1')
    a2_f = result7.best_values.get('a2')
    a5_f = result7.best_values.get('a5')
    a6_f = result7.best_values.get('a6')
    
#    Get the extrema for edge height fitting
    fitted_data = result7.best_fit
#     x =np.linspace(0,len(fitted_data), len(fitted_data))
#     result_firstpart = ModelFirstPart(t=x,a1=a1_f,a2=a2_f,a6=a6_f)
#     result_secondpart = ModelSecondPart(t=x, a2=a2_f, a5=a5_f, a6=a6_f)
#     result_thirdpart = ModelThirdPart(t=x, t0=t0_f, sigma=sigma_f, alpha=alpha_f)
    
    pos_extrema = []
    
    ## This does not work all the time..
#     step_function = B(t,t0_f,alpha_f,sigma_f)
#     min_pos = find_last(step_function,0.0)
#     pos_extrema.append(min_pos)
#     max_pos = find_first(step_function,0.99)
#     pos_extrema.append(max_pos)

# I try with Florencia-s implementation
    
    if (bool_linear):  
        fit_before = line_before(t,a5_f,a6_f)
        fit_after = line_afte(t,a1_f,a2_f)
    else:
        fit_before = exp_combined(t,a1_f,a2_f,a5_f,a6_f)
        fit_after = exp_after(t,a1_f,a2_f)
    
    index_t0 = find_nearest(t,t0_f)
    pos_extrema.append(fit_before[index_t0])
    pos_extrema.append(fit_after[index_t0])
    # it is actually not a position......

    
    plt.figure()
    plt.plot(t, mybragg, 'b-')
#     plt.plot(t, result7.init_fit, 'k--')
    plt.plot(t, result7.best_fit, 'r-', linewidth='1.2')
    plt.plot(t, result1.best_fit, 'k--')
    plt.plot(t, result1.init_fit, 'r--')
    plt.plot(t, result2.best_fit, '--')
    plt.plot(t, result3.best_fit, '--')
    plt.plot(t, result4.best_fit, '--')
    plt.plot(t, result5.best_fit, '--')
    plt.plot(t, result6.best_fit, '--')
    
    
    plt.plot(t0_f,result7.best_fit[index_t0],'ok')
    plt.plot(t0_f, fit_before[index_t0],'ok')
    plt.plot(t0_f, fit_after[index_t0],'ok')
#     plt.plot(t,step_function,'--k')
    plt.title('edge fitting and estimated edge position')
#     plt.plot(t0_f, result7.best_fit[np.where(t==t0_f)],'ok')
    plt.show()
    
    if (bool_print):
        print(result1.fit_report())
        print(result2.fit_report())
        print(result3.fit_report())
        print(result4.fit_report())
        print(result5.fit_report())
        print(result6.fit_report())
        
    
    return {'t0':t0_f, 'sigma':sigma_f, 'alpha':alpha_f, 'a1':a1_f, 'a2':a2_f,'a5':a5_f, 'a6':a6_f, 'final_result':result7, 'fitted_data':fitted_data, 'pos_extrema':pos_extrema}

    