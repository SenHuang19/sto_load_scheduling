cd(dirname(@__FILE__))
include("opt_main_det_test.jl")

using JSON
using CSV
using DataFrames
using .Controller

clearconsole()
rawdf = CSV.read(string("SmallOffice.csv"), DataFrame)
Toa = rawdf[!,Symbol("Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)")][1:end];
Tzon1 = rawdf[!,Symbol("SOUTH PERIM SPC GS1:Zone Mean Air Temperature [C](TimeStep)")][1:end];
Tzon2 = rawdf[!,Symbol("EAST PERIM SPC GE2:Zone Mean Air Temperature [C](TimeStep)")][1:end];
Tzon3 = rawdf[!,Symbol("NORTH PERIM SPC GN3:Zone Mean Air Temperature [C](TimeStep)")][1:end];
Tzon4 = rawdf[!,Symbol("WEST PERIM SPC GW4:Zone Mean Air Temperature [C](TimeStep)")][1:end];
Tzon5 = rawdf[!,Symbol("CORE SPC GC5:Zone Mean Air Temperature [C](TimeStep)")][1:end];

Tzon6 = rawdf[!,Symbol("SOUTH PERIM SPC TS11:Zone Mean Air Temperature [C](TimeStep)")][1:end];
Tzon7 = rawdf[!,Symbol("EAST PERIM SPC TE12:Zone Mean Air Temperature [C](TimeStep)")][1:end];
Tzon8 = rawdf[!,Symbol("NORTH PERIM SPC TN13:Zone Mean Air Temperature [C](TimeStep)")][1:end];
Tzon9 = rawdf[!,Symbol("WEST PERIM SPC TW14:Zone Mean Air Temperature [C](TimeStep)")][1:end];
Tzon10 = rawdf[!,Symbol("CORE SPC TC15:Zone Mean Air Temperature [C](TimeStep)")][1:end];

TSzon1 = rawdf[!,Symbol("SOUTH PERIM SPC GS1:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];
TSzon2 = rawdf[!,Symbol("EAST PERIM SPC GE2:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];
TSzon3 = rawdf[!,Symbol("NORTH PERIM SPC GN3:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];
TSzon4 = rawdf[!,Symbol("WEST PERIM SPC GW4:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];
TSzon5 = rawdf[!,Symbol("CORE SPC GC5:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];

TSzon6 = rawdf[!,Symbol("SOUTH PERIM SPC TS11:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];
TSzon7 = rawdf[!,Symbol("EAST PERIM SPC TE12:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];
TSzon8 = rawdf[!,Symbol("NORTH PERIM SPC TN13:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];
TSzon9 = rawdf[!,Symbol("WEST PERIM SPC TW14:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];
TSzon10 = rawdf[!,Symbol("CORE SPC TC15:Zone Thermostat Cooling Setpoint Temperature [C](TimeStep)")][1:end];

csv_file_result = "output.csv"
for t = 1:1:1440

    ################### generate dict; no be need in our tool ######################
    GUI_input = Dict("OutdoorAirTemperature" => Toa[t],
                "Time"    => t,
                "forecast"=> Toa[t+60:60:t+24*60],
                "Tzon1"   => Tzon1[t],
                "Tzon2"   => Tzon2[t],
                "Tzon3"   => Tzon3[t],
                "Tzon4"   => Tzon4[t],
                "Tzon5"   => Tzon5[t],
                "Tzon6"   => Tzon6[t],
                "Tzon7"   => Tzon7[t],
                "Tzon8"   => Tzon8[t],
                "Tzon9"   => Tzon9[t],
                "Tzon10"  => Tzon10[t],
                "TSzon1"  => TSzon1[t+60:60:t+24*60],
                "TSzon2"  => TSzon2[t+60:60:t+24*60],
                "TSzon3"  => TSzon3[t+60:60:t+24*60],
                "TSzon4"  => TSzon4[t+60:60:t+24*60],
                "TSzon5"  => TSzon5[t+60:60:t+24*60],
                "TSzon6"  => TSzon6[t+60:60:t+24*60],
                "TSzon7"  => TSzon7[t+60:60:t+24*60],
                "TSzon8"  => TSzon8[t+60:60:t+24*60],
                "TSzon9"  => TSzon9[t+60:60:t+24*60],
                "TSzon10" => TSzon10[t+60:60:t+24*60]);
    # GUI_input = JSON.parsefile("input.json")  # parse and transform data
    ########################### call optimization ##################################


    result = Controller.run(GUI_input)

    if t == 1
        CSV.write(csv_file_result, result, append=false)
    else
        CSV.write(csv_file_result, result, append=true)
    end
    # json_file_result = "output.json"
    # open(json_file_result, "w") do f
    #     JSON.print(f, result, 4)
    # end
end
