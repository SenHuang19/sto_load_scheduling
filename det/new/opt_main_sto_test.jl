module Controller
include("opt_engine_stoch.jl")
using .Opt_engine

using CSV
using DataFrames
using Statistics
# using Dates
# using MAT

function run(GUI_input::Dict)

    ###### read inputs ######

    for (key, value) in GUI_input
        @eval $(Symbol(key)) = $value
    end
	###### Inputs ######
	N = 31 				# number of days for simulation
	Delta_T = 1;	 	# prediction resolution in min,
	# Tr = 24;     		# Tzon Setpoint in C
	dT_m  = 1; # model prediction interval in hour (Optimization based only)
	Tbd = 0.5; # bandwidth of T bounds around Tsetpoint

	solverflag = 2; 		# 1 for the 1st-order RC model
	uncertoat_flag = 0; # 0 for determinstic case of Toa, 1 for stochastic case of Toa
	uncertzon_flag = 1; # 0 for determinstic case of Tout, 1 for stochastic case of Tout
	optcost_flag = 1;	# enable price profile in the cost function
	# sto_model_flag = 0; # 1 if stochastic variables' distributions are known, 0 otherwise
	debugflag = 1;
	numrl = 58;        # number of scenarios for stochastic programming

	numzones = 10 		# Number of zones in building
	numcoeffs = 4 		# Number of coefficients of zone-temp model

	min_idx = repeat(1:Int(24*60), N+1)
	# hour_idx = repeat(repeat(1:24, inner=60),N+1)

# Pcmin = [215.7352677 215.7352677 215.7352677 215.7352677 1180 215.7352677 215.7352677 215.7352677 215.7352677 1180];# min 0
# Pcmin = [0 0 0 0 0 0 0 0 0 0];# min 0
# Pcmax = [1294.411606 1294.411606 1294.411606 1294.411606 7080 1294.411606 1294.411606 1294.411606 1294.411606 7080];
# Phmin = [0 0 0 0 0 0 0 0 0 0];
# Phmax = [1294.411606 1294.411606 1294.411606 1294.411606 7080 1294.411606 1294.411606 1294.411606 1294.411606 7080];
	StartTime = 3540
	if Time == StartTime
		t = 60;
	else
		t = Int(ceil.((Time - StartTime)/60))+60;
	end


	# Timestamp = 1:(N*24*60/Delta_T); # Simulation timestamp
	# Ntime = length(Timestamp) # length of timestamps
	# Ncontrol = round(Int,Ntime/60/dT_m); # number of control data
	Npred = round(Int,24/dT_m); # Length of prediction horizon
	Tzon_sto = zeros(numzones,Npred, numrl);
	# if uncertzon_flag == 1
	# 	for i = 1:numrl
	# 		sto_Data_file = string("Data/Sto_scenarios/Tz_n_sto$(i).csv");
	# 		# println("$i th case")
	# 		if (t%10080)==0
	# 			Tzon_sto[:,:,i] = reshape(CSV.read(sto_Data_file, DataFrame)[!, "10080"][1:end],Npred,numzones)';
	# 		else
	# 			Tzon_sto[:,:,i] = reshape(CSV.read(sto_Data_file, DataFrame)[!, "$(t%10080)"][1:end],Npred,numzones)';
	# 		end
	# 		# Tzon_sto[:,:,i] = reshape(CSV.read(sto_Data_file, DataFrame)[!, "$t"][1:end],numzones,Npred);
	# 	end
	# end
	if uncertzon_flag == 1
		for i = 1:numrl
			sto_Data_file = string("Data/Scenarios_new/Tz_n_sto$(i).csv");
			# println("$i th case")
			Tzon_sto[:,:,i] = reshape(CSV.read(sto_Data_file, DataFrame)[!, "Tdelta"][1:end],Npred,numzones)';
			# print(Tzon_sto)
			# Tzon_sto[:,:,i] = reshape(CSV.read(sto_Data_file, DataFrame)[!, "$t"][1:end],numzones,Npred);
		end
	end

	Tr = zeros(numzones,Int(24/dT_m))
	T_oa = OutdoorAirTemperature;
	T_S2 = mean(Tzon1);
	T_E2 = mean(Tzon2);
	T_N2 = mean(Tzon3);
	T_W2 = mean(Tzon4);
	T_C2 = mean(Tzon5);
	T_S1 = mean(Tzon6);
	T_E1 = mean(Tzon7);
	T_N1 = mean(Tzon8);
	T_W1 = mean(Tzon9);
	T_C1 = mean(Tzon10);
	Tr[1,:] = Trzon1;
	Tr[2,:] = Trzon2;
	Tr[3,:] = Trzon3;
	Tr[4,:] = Trzon4;
	Tr[5,:] = Trzon5;
	Tr[6,:] = Trzon6;
	Tr[7,:] = Trzon7;
	Tr[8,:] = Trzon8;
	Tr[9,:] = Trzon9;
	Tr[10,:] = Trzon10;
	T_oa_p = forecast;

	T_zon0 = [T_S2 T_E2 T_N2 T_W2 T_C2 T_S1 T_E1 T_N1 T_W1 T_C1];

	price = CSV.read(string("prices_profile.csv"), DataFrame)[!,Symbol("price")][1:end];
	price[721:1080] = price[721:1080].*2; # Double the price during occupied period(12pm to 18pm)

	Coeffs_file = string("linear_coefs_avg.csv");
	coeffs = zeros(numzones,numcoeffs)
	Pm = zeros(numzones)
	for z = 1:numzones
		for k = 1:numcoeffs
			coeffs[z,k] = CSV.read(Coeffs_file, DataFrame)[!,Symbol("$z")][k];
		end
		Pm[z] = 1000*CSV.read(Coeffs_file, DataFrame)[!,Symbol("$z")][end]; 	# kW
	end

	# Tzmin = Tr.-dband;
	Tzmax = Tr;
	# Simulation time in minutes
	global Tinit = T_zon0;
	# # Tinit = repeat(Tinit, Int(numzones/10));
	# global u_t = zeros(numzones)
	# global Opcost = zeros(1,Ntime)
	global Pc_p = zeros(numzones)
	global Tzon_p = zeros(numzones)
	# global cputime = 0;
	# global dT = Delta_T/60; # Delta_T in hour
	################################################################################
	#		RUN Optimization for power scheduling with price profile
	################################################################################
	global Optimization_input = Dict("numzones" => numzones,
	"coeffs"=>coeffs,
	"Pm" 	=> Pm,
	"price" => price,
	"min_idx"=>min_idx,
	# "hour_idx"=>hour_idx,
	"Delta_T"=>Delta_T,
	"dT" 	=> dT_m,
	"t_0"	=> t,
	"T_init"=> Tinit,
	"T_oa"  => T_oa,
	"T_oa_p" => T_oa_p,
	"Tz_n_sto"=>Tzon_sto,
	"Tbd"   => Tbd,
	# "Tzmin" => Tzmin,
	"Tzmax" => Tzmax,
	"solverflag"=>solverflag,
	"uncertoat_flag"=>uncertoat_flag,
	"uncertzon_flag"=>uncertzon_flag,
	"optcost_flag"  =>optcost_flag,
	# "sto_model_flag"=>sto_model_flag,
	"debugflag"     =>debugflag,
	"numrl" 		=>numrl);

	global sol = Opt_engine.run(Optimization_input)
	for z = 1:numzones
		Pc_p[z] = sol[!,r"p_c"][2,z]*Pm[z];
		Tzon_p[z] = sol[!,r"tzon"][2,z];
		# Pc_p_store[z,Int(ceil(t/60/dT_m))] = Pc_p[z];
	end
	println("Output power target:  \n\t",Pc_p)
	println("Next Temperature prediction: \n\t",Tzon_p)
	# uncontrolled_power = CSV.read(string("rest_loadpower.csv"), DataFrame)[!,Symbol("Hourlypower")][Int(ceil(t/60))];
	# result = Dict("demand_target"=>sum(Pc_p[z] for z=1:numzones)+uncontrolled_power);
	result = Dict("demand_target"=>sum(Pc_p[z] for z=1:numzones))
	for z = 1:numzones
		result["HP$z"] = Pc_p[z];
	end
	df_result = DataFrame(ts = Time, demand_target = result["demand_target"])

	if debugflag == 1
		if Time == StartTime
			CSV.write("saved/output.csv", df_result, append=false)
		else
			CSV.write("saved/output.csv", df_result, append=true)
		end
		CSV.write("saved/sol_T$t.csv", sol, append=false)
		return result
	end

end
end
