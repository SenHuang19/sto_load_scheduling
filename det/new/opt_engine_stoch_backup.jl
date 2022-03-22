module Opt_engine

using Clp
# using Ipopt
using JuMP
using DataFrames
# using Conda
# using PyCall
using ScikitLearn
# Conda.add("nomkl")
# Conda.add("joblib")
# Conda.add("scikit-learn")
# Conda.rm("mkl")
cd(dirname(@__FILE__))



function run(GUI_input::Dict)

    ###### read inputs ######

    for (key, value) in GUI_input
        @eval $(Symbol(key)) = $value
    end

    ###### Chiller power Optimal Scheduling ######

    # looking at a 24-hour-ahead time window for the optimal scheduling
    H = Int(24/dT);
    t0 = Int(t_0); # start timestamp in minute
    if solverflag == 1
        m = Model(Cbc.Optimizer);
        set_optimizer_attribute(m, "logLevel", 1)
        # set_optimizer_attribute(m, "ratioGap", 0.03)
        # set_optimizer_attribute(m, "threads", 4)
        # set_optimizer_attribute(m, "seconds", 1000)
    elseif solverflag == 2
        m = Model(Clp.Optimizer);
        set_optimizer_attribute(m, "LogLevel", 1);
    end
    # m = Model(Clp.Optimizer);
    # set_optimizer_attribute(m, "LogLevel", 0);

    # @variable(m, p_c[z = 1:numzones, t = 1:H], Bin);   # hourly chiller power (Binary variable)
    @variable(m, p_c[z = 1:numzones, t = 1], lower_bound = 0, upper_bound = 1);   # next chiller power (normalized between 0 and 1)
    @variable(m, slack_u[z = 1:numzones, t = 1:H] >= 0.0)
    @variable(m, slack_d[z = 1:numzones, t = 1:H] >= 0.0)
	@variable(m, p_c_p[z = 1:numzones, t = 2:H, k = 1:numrl], lower_bound = 0, upper_bound = 1);   # future hourly chiller power(normalized between 0 and 1)
    @variable(m, Tzon[z = 1:numzones,t = 1:H, k = 1:numrl]);   # hourly zone temperatures(unit in C)
	# if uncertoat_flag == 0
	# 	@expression(m, T_oa_p[t=1:H], T_oa[t0+Int((t-1)*60*dT)])
	# 	@expression(m, T_oa_s[t=1:H,r=1:numrl], T_oa[t0+Int((t-1)*60*dT)])
	# elseif uncertoat_flag == 1
	# 	@expression(m, T_oa_p[t=1:H], T_oap[t])
	# 	@expression(m, T_oa_s[t=1:H,r=1:numrl], T_oa_sto[t,r])
	# end
	
	if uncertzon_flag == 1
		# T_offset = rand(numzones,H)*2;
		for rl_idx = 1:numrl
	        @constraint(m, [z=1:numzones, t=1], Tzon[z,t,rl_idx] == coeffs[z,4]+coeffs[z,3]*T_init[z]+coeffs[z,2]*T_oa_p[t] + coeffs[z,1]*Pm[z]*p_c[z,t])
	        @constraint(m, [z=1:numzones, t=2:H], Tzon[z,t,rl_idx] == coeffs[z,4]+coeffs[z,3]*Tzon[z,t-1,rl_idx]+coeffs[z,2]*T_oa_p[t] + coeffs[z,1]*Pm[z]*p_c_p[z,t,rl_idx])
            @constraint(m, [z=1:numzones, t=1:H], Tzon[z,t,rl_idx] + Tz_n_sto[z,t,rl_idx] <= Tzmax[z,t]+Tbd+slack_u[z,t]) # upper bound
            @constraint(m, [z=1:numzones, t=1:H], Tzon[z,t,rl_idx] + Tz_n_sto[z,t,rl_idx] >= 22.8-Tbd-slack_d[z,t]) # lower bound
		end
	end


    # # Force heat power to be zero
    # @constraint(m, heater_cons[z = 1:numzones, t=1:H], p_h[z,t] == 0.0)
    penalty_u = 1e5;
    penalty_d = 1e3;
    if optcost_flag == 1
		@expression(m, pr[t=1:H], price[min_idx[t0+Int(t*60*dT)]])
		# for tt = 1:H
		# 	println(price[min_idx[t0+Int((tt-1)*60*dT)]])
		# end
		@objective(m, Min, sum(pr[1]*Pm[z]*p_c[z,1] for z=1:numzones) + sum(pr[t]*Pm[z]*p_c_p[z,t,r] for z=1:numzones, t=2:H, r = 1:numrl)/numrl + sum(penalty_u*slack_u[z,t]+penalty_d*slack_d[z,t] for z = 1:numzones, t = 1:H));
        # @objective(m, Min, sum(prob_rl[t]*pr[t]/CoP[z]/R[z]*T_oa_p[t,k] for z=1:numzones, t=1:H, k=1:numrl) +
		# 			sum(prob_rl[t]*pr[t]*C[z]/dT/CoP[z]*((1-dT/C[z]/R[z])*Tzon[z,t-1,k] - Tzon[z,t,k]) for z=1:numzones, t=2:H, k=1:numrl)-
		# 			sum(prob_rl[1]*pr[1]*C[z]/dT/CoP[z]*Tzon[z,1,k] for z=1:numzones, k=1:numrl));
    else
        @objective(m, Min, sum((Pm[z]*p_c[z,t]) for z=1:numzones, t=1:H)+penalty*sum(slack[z,t]^2 for z = 1:numzones, t = 1:H));
    end

    status = optimize!(m);
    println("Optimal scheduling for hour ", Int(ceil(t0/60)), " -- Status: ", termination_status(m));
	sol_p_c = zeros(numzones,H)
    sol_p_c[:,1] = JuMP.value.(p_c); # println(sol_p_c);
	P_c_rl = JuMP.value.(p_c_p);
	for z = 1:numzones, t = 2:H
		sol_p_c[z,t] = sum(P_c_rl[z,t,k] for k=1:numrl)/numrl
	end
	println(sol_p_c)
    Tzon_rl = JuMP.value.(Tzon); # println(sol_tzon);
	sol_tzon = zeros(numzones,H)
	for z = 1:numzones, t = 1:H
		sol_tzon[z,t] = sum(Tzon_rl[z,t,k] for k =1:numrl)/numrl
	end

    sol_pr = JuMP.value.(pr);
    sol_slack_u = JuMP.value.(slack_u);
    sol_slack_d = JuMP.value.(slack_d);
    # sol_cost = sum(sol_pr.*(Pm[z]*sol_p_c[z,:]) for z=1:numzones)
    sol_cost1 = sum(sol_slack_u[z,t] for z=1:numzones, t=1:H)
    sol_cost2 = sum(sol_slack_u[z,t]+sol_slack_d[z,t] for z = 1:numzones, t = 1:H)
    println(sol_cost1)
    println(sol_cost2)

    sol_Tz_upp = Tzmax .+ Tbd .+ sol_slack_u
    sol_Tz_low = 22.8 - Tbd .- sol_slack_d

    if debugflag == 1
        result1 = DataFrame()
        result2 = DataFrame()
        result3 = DataFrame()
        result4 = DataFrame()
        result5 = DataFrame()
        result6 = DataFrame()
        result7 = DataFrame()
        result8 = DataFrame()
        default_Values = -100000;
        Tz_n_sto_avg = zeros(numzones,H)
        for z = 1:numzones, t = 1:H
            Tz_n_sto_avg[z,t] = sum(Tz_n_sto[z,t,k] for k =1:numrl)/numrl
        end
        for z = 1:Int(numzones)
            insertcols!(result1,z,Symbol("sol_p_c_$z")=>vcat(default_Values,sol_p_c[z,:]))
            insertcols!(result2,z,Symbol("sol_tzon_$z")=>vcat(T_init[z],sol_tzon[z,:]))
            insertcols!(result3,z,Symbol("sol_slack_u_$z")=>vcat(default_Values,sol_slack_u[z,:]))
            insertcols!(result4,z,Symbol("sol_slack_d_$z")=>vcat(default_Values,sol_slack_d[z,:]))
            insertcols!(result5,z,Symbol("Tsp_$z") =>vcat(default_Values,Tzmax[z,:]))
            insertcols!(result6,z,Symbol("Tupp_$z")=>vcat(default_Values,sol_Tz_upp[z,:]))
            insertcols!(result7,z,Symbol("Tlow_$z")=>vcat(default_Values,sol_Tz_low[z,:]))
            insertcols!(result8,z,Symbol("Tdelta_$z")=>vcat(default_Values,Tz_n_sto_avg[z,:]))
        end
        result0 = DataFrame(price = vcat(price[min_idx[t0]], sol_pr), OutdoorTemperature = vcat(T_oa,T_oa_p))
        result = hcat(result0,result1,result2,result3,result4,result5,result6,result7,result8)
    end
	# println(T_noise)
    return result;

end
end
