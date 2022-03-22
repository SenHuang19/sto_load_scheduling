module Opt_engine

using Clp
# using Ipopt
# using ECOS
using JuMP
using DataFrames
using CSV
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
        m = Model(Ipopt.Optimizer);
        set_optimizer_attribute(m, "logLevel", 1)
        set_optimizer_attribute(m, "ratioGap", 0.03)
        set_optimizer_attribute(m, "threads", 4)
        set_optimizer_attribute(m, "seconds", 1000)
    elseif solverflag == 2
        m = Model(Clp.Optimizer);
        set_optimizer_attribute(m, "LogLevel", 1);
    end
    # m = Model(Clp.Optimizer);
    # set_optimizer_attribute(m, "LogLevel", 0);

	# T_noise = zeros(H)

    # @variable(m, p_c[z = 1:numzones, t = 1:H], Bin);   # hourly chiller power (Binary variable)
    @variable(m, p_c[z = 1:numzones, t = 1:H], lower_bound = 0, upper_bound = 1);   # hourly chiller power (Binary variable)
	@variable(m, slack_u[z = 1:numzones, t = 1:H] >= 0.0)
    @variable(m, slack_d[z = 1:numzones, t = 1:H] >= 0.0)
    @variable(m, Tzon[z = 1:numzones,t = 1:H])   # hourly zone temperatures(unit in C)
	@constraint(m, maxcomfort_cons[z=1:numzones, t=1:H], Tzon[z,t] <= Tzmax[z,t]+Tbd+slack_u[z,t])
    @constraint(m, mincomfort_cons[z=1:numzones, t=1:H], Tzon[z,t] >= 22.8-Tbd-slack_d[z,t])

	if  uncertout_flag == 0
        @constraint(m, zon_temp_cons_init[z=1:numzones, t=1], Tzon[z,t] == coeffs[z,4] + coeffs[z,3]*T_init[z]+coeffs[z,2]*(T_oa_p[t]) + coeffs[z,1]*Pm[z]*p_c[z,t])
        @constraint(m, zon_temp_cons[z=1:numzones, t=2:H], Tzon[z,t] == coeffs[z,4] + coeffs[z,3]*Tzon[z,t-1]+coeffs[z,2]*(T_oa_p[t]) + coeffs[z,1]*Pm[z]*p_c[z,t])
	elseif uncertout_flag == 1
		@constraint(m, zon_temp_cons_init[z=1:numzones, t=1], Tzon[z,t] == coeffs[z,4] + coeffs[z,3]*T_init[z]+coeffs[z,2]*(T_oa_p[t]) + coeffs[z,1]*Pm[z]*p_c[z,t] + Tz_n[z,t])
        @constraint(m, zon_temp_cons[z=1:numzones, t=2:H], Tzon[z,t] == coeffs[z,4] + coeffs[z,3]*Tzon[z,t-1]+coeffs[z,2]*(T_oa_p[t]) + coeffs[z,1]*Pm[z]*p_c[z,t] + Tz_n[z,t])
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
        @objective(m, Min, sum(pr[t]*(Pm[z]*p_c[z,t]) for z=1:numzones, t=1:H)+sum(penalty_u*slack_u[z,t]+penalty_d*slack_d[z,t] for z = 1:numzones, t = 1:H));
        # @objective(m, Min, sum((p_c[z,t]+p_h[z,t]) for z=1:numzones, t=1:H));
    else
        @objective(m, Min, sum((Pm[z]*p_c[z,t]) for z=1:numzones, t=1:H)+penalty*sum(slack[z,t]^2 for z = 1:numzones, t = 1:H));
    end

    status = optimize!(m);
    println("Optimal scheduling for minute ", Int(t0), " -- Status: ", termination_status(m));
    sol_p_c = JuMP.value.(p_c); # println(sol_p_c);
    sol_tzon = JuMP.value.(Tzon); # println(sol_tzon);
    sol_pr = JuMP.value.(pr);
    sol_slack_u = JuMP.value.(slack_u);
    sol_slack_d = JuMP.value.(slack_d);
    # sol_cost = sum(sol_pr.*(Pm[z]*sol_p_c[z,:]) for z=1:numzones)
    sol_cost = sum(sol_pr[t]*(Pm[z]*sol_p_c[z,t]) for z=1:numzones,t=1:H)
    sol_cost1 = sum(sol_slack_u[z,t] for z=1:numzones, t=1:H)
    sol_cost2 = sum(sol_slack_u[z,t]+sol_slack_d[z,t] for z = 1:numzones, t = 1:H)
    println(sol_cost)
    println(sol_cost1)
    println(sol_cost2)

    sol_Tz_upp = Tzmax .+ Tbd .+ sol_slack_u
    sol_Tz_low = 22.8 - Tbd .- sol_slack_d
    # println("Upper bound:",sol_Tz_upp)
    # println("Lower bound", sol_Tz_low)
    df_cost = DataFrame(t0 = t0, cost = sol_cost, cost1 = sol_cost1, cost2 = sol_cost2)
    CSV.write("saved_cost.csv", df_cost, append=true)
    # result = DataFrame(
    # sol_p_c_1 = sol_p_c[1,:],
    # sol_p_c_2 = sol_p_c[2,:],
    # sol_p_c_3 = sol_p_c[3,:],
    # sol_p_c_4 = sol_p_c[4,:],
    # sol_p_c_5 = sol_p_c[5,:],
    # sol_p_c_6 = sol_p_c[6,:],
    # sol_p_c_7 = sol_p_c[7,:],
    # sol_p_c_8 = sol_p_c[8,:],
    # sol_p_c_9 = sol_p_c[9,:],
    # sol_p_c_10= sol_p_c[10,:],
    # # sol_p_h_1 = POW_h[1,:],
    # # sol_p_h_2 = POW_h[2,:],
    # # sol_p_h_3 = POW_h[3,:],
    # # sol_p_h_4 = POW_h[4,:],
    # # sol_p_h_5 = POW_h[5,:],
    # # sol_p_h_6 = POW_h[6,:],
    # # sol_p_h_7 = POW_h[7,:],
    # # sol_p_h_8 = POW_h[8,:],
    # # sol_p_h_9 = POW_h[9,:],
    # # sol_p_h_10 = POW_h[10,:],
    # sol_tzon_1 = sol_tzon[1,:],
    # sol_tzon_2 = sol_tzon[2,:],
    # sol_tzon_3 = sol_tzon[3,:],
    # sol_tzon_4 = sol_tzon[4,:],
    # sol_tzon_5 = sol_tzon[5,:],
    # sol_tzon_6 = sol_tzon[6,:],
    # sol_tzon_7 = sol_tzon[7,:],
    # sol_tzon_8 = sol_tzon[8,:],
    # sol_tzon_9 = sol_tzon[9,:],
    # sol_tzon_10= sol_tzon[10,:]);
    result1 = DataFrame()
    result2 = DataFrame()
    result3 = DataFrame()
    result4 = DataFrame()
    result5 = DataFrame()
    result6 = DataFrame()
    result7 = DataFrame()
    default_Values = -100000;
    for z = 1:Int(numzones)
        insertcols!(result1,z,Symbol("sol_p_c_$z") =>vcat(default_Values,sol_p_c[z,:]))
        insertcols!(result2,z,Symbol("sol_tzon_$z")=>vcat(T_init[z],sol_tzon[z,:]))
        insertcols!(result3,z,Symbol("sol_slack_u_$z")=>vcat(default_Values,sol_slack_u[z,:]))
        insertcols!(result4,z,Symbol("sol_slack_d_$z")=>vcat(default_Values,sol_slack_d[z,:]))
        insertcols!(result5,z,Symbol("Tsp_$z") =>vcat(default_Values,Tzmax[z,:]))
        insertcols!(result6,z,Symbol("Tupp_$z")=>vcat(default_Values,sol_Tz_upp[z,:]))
        insertcols!(result7,z,Symbol("Tlow_$z")=>vcat(default_Values,sol_Tz_low[z,:]))
    end
    result0 = DataFrame(price = vcat(price[min_idx[t0]], sol_pr), OutdoorTemperature = vcat(T_oa,T_oa_p))
    result = hcat(result0,result1,result2,result3,result4,result5,result6,result7)
	# println(T_noise)
    return result;

end
end
