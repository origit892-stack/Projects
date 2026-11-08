#!/usr/bin/env python3
"""Static presentation around runtime-authored FarmingSystem anchors."""
from __future__ import annotations
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from new_bunker.environment_rework import asset
from new_bunker.kit import CONCRETE_DARK, GREEN, LIGHT_COLD, LIGHT_WARM, RUST, STEEL, STEEL_LIGHT, UTILITY_BLUE, WOOD, YELLOW, fluorescent, model, part, pipe, point_light

OUT=Path(__file__).resolve().parents[2]/'src/Workspace/FarmingEnvironment.model.json'

def build():
    children=[]
    # Iteration 3 farm-yard language: cover the bright terrain visually without touching runtime plot anchors.
    children.append(model('FarmGroundAndTransition',[
        part('FarmEarthPad',(35.0,0.22,25.0),(66.5,56.72,215.0),material='Ground',color=[0.20,0.18,0.135],collide=False),
        part('DampConcreteServiceApron',(12.0,0.25,12.0),(82.5,56.74,215.0),material='Concrete',color=[0.22,0.235,0.225],collide=False),
        part('BunkerFarmTransitionTrack',(15.0,0.20,9.0),(49.0,56.70,202.0),material='Concrete',color=[0.25,0.245,0.22],collide=False,rot=(0,-8,0)),
        part('TransitionMudA',(7.5,0.025,3.5),(51.5,56.86,204.0),material='Ground',color=[0.13,0.12,0.09],collide=False,transparency=0.08,rot=(0,8,0)),
        part('TransitionMudB',(5.5,0.025,2.8),(47.0,56.86,200.0),material='Ground',color=[0.16,0.14,0.10],collide=False,transparency=0.12,rot=(0,-11,0)),
        part('WestRetainingEdge',(0.55,1.0,25.0),(49.2,57.1,215.0),material='Concrete',color=[0.28,0.29,0.27]),
        part('NorthRetainingEdge',(35.0,1.0,0.55),(66.5,57.1,227.2),material='Concrete',color=[0.28,0.29,0.27]),
        part('SouthRetainingEdge',(35.0,1.0,0.55),(66.5,57.1,202.8),material='Concrete',color=[0.28,0.29,0.27]),
        part('DrainageGravelWest',(2.0,0.12,22.0),(50.5,56.88,215.0),material='Pebble',color=[0.20,0.21,0.19],collide=False),
        part('DrainageGravelEast',(2.0,0.12,22.0),(79.0,56.88,215.0),material='Pebble',color=[0.20,0.21,0.19],collide=False),
    ]))
    planter=[]
    for row,z in enumerate((209.0,215.0,221.0),1):
        for col,x in enumerate((55.0,61.0,67.0,73.0,79.0),1):
            n=f'R{row}C{col}'
            # Four low rails frame each canonical 3x3 Plot but never overlap its playable top.
            planter += [
                part('Planter'+n+'West',(0.28,0.75,3.8),(x-1.75,57.15,z),material='Metal',color=[0.21,0.245,0.22],collide=False),
                part('Planter'+n+'East',(0.28,0.75,3.8),(x+1.75,57.15,z),material='Metal',color=[0.21,0.245,0.22],collide=False),
                part('Planter'+n+'North',(3.2,0.75,0.28),(x,57.15,z+1.75),material='WoodPlanks',color=[0.255,0.205,0.145],collide=False),
                part('Planter'+n+'South',(3.2,0.75,0.28),(x,57.15,z-1.75),material='WoodPlanks',color=[0.255,0.205,0.145],collide=False),
            ]
    children.append(model('ImprovisedPlanterConstruction',planter))
    children.append(model('IrrigationDistribution',[
        pipe('RowHeaderNorth',(66.5,59.1,209.0),27.0,'x',0.18,UTILITY_BLUE),
        pipe('RowHeaderCenter',(66.5,59.1,215.0),27.0,'x',0.18,UTILITY_BLUE),
        pipe('RowHeaderSouth',(66.5,59.1,221.0),27.0,'x',0.18,UTILITY_BLUE),
        part('NorthHeaderSupport',(0.30,2.0,0.30),(53.0,58.2,209.0),material='Metal',color=STEEL_LIGHT,collide=False),
        part('CenterHeaderSupport',(0.30,2.0,0.30),(53.0,58.2,215.0),material='Metal',color=STEEL_LIGHT,collide=False),
        part('SouthHeaderSupport',(0.30,2.0,0.30),(53.0,58.2,221.0),material='Metal',color=STEEL_LIGHT,collide=False),
    ]))
    children.append(model('FarmWaterUtilityFrame',[
        part('WaterFrameWest',(0.45,7.0,0.45),(51.0,60.0,203.8),material='Metal',color=STEEL_LIGHT),
        part('WaterFrameEast',(0.45,7.0,0.45),(80.0,60.0,203.8),material='Metal',color=STEEL_LIGHT),
        part('WaterFrameHeader',(29.5,0.45,0.45),(65.5,63.3,203.8),material='Metal',color=STEEL_LIGHT),
        pipe('PrimaryRecoveredWaterMain',(65.5,62.65,203.9),28.0,'x',0.42,UTILITY_BLUE),
        pipe('FieldFeedWest',(53.0,60.2,213.5),18.0,'z',0.26,UTILITY_BLUE),
        pipe('FieldFeedEast',(79.0,60.2,213.5),18.0,'z',0.26,UTILITY_BLUE),
        asset('PrimaryWaterIsolation','valve',(52.0,61.0,203.8),(2.5,1.8,1.6),(0,0,0)),
        asset('WaterControlJunction','junction',(78.5,61.0,203.5),(2.4,2.3,0.95),(0,0,0)),
    ]))
    # Plot field: low perimeter infrastructure keeps every 3x3 gameplay plot unobstructed.
    children.append(model('PlotFieldInfrastructure',[
        part('WestIrrigationCurb',(0.45,0.55,17.0),(51.8,57.15,215),material='CorrodedMetal',color=STEEL),
        part('EastServiceCurb',(0.45,0.55,17.0),(81.2,57.15,215),material='CorrodedMetal',color=STEEL),
        asset('IrrigationMain','rusty_pipe',(51.6,58.0,215),(0.48,0.48,17.5),(0,90,0)),
        asset('IrrigationValve','valve',(51.7,58.2,207.0),(2.4,1.8,1.6),(0,90,0)),
        asset('FieldJunctionBox','junction',(81.25,59.0,207.5),(2.4,2.3,0.95),(0,-90,0)),
        asset('FieldVentGrille','vent',(81.15,60.5,222.8),(3.2,2.8,0.58),(0,-90,0)),
        part('NorthDrain',(30.0,0.12,0.7),(66.5,56.95,224.2),material='DiamondPlate',color=STEEL_LIGHT,collide=False),
        part('SouthDrain',(30.0,0.12,0.7),(66.5,56.95,205.8),material='DiamondPlate',color=STEEL_LIGHT,collide=False),
        part('WetServiceLane',(3.0,0.018,17.0),(80.2,56.91,215),material='Glass',color=[0.05,0.08,0.07],collide=False,transparency=0.72,cast_shadow=False),
        part('WestPlanterFrame',(0.30,0.9,18.0),(53.0,57.4,215),material='CorrodedMetal',color=STEEL,collide=False),
        part('CentralWaterHeader',(25.0,0.28,0.28),(66.5,61.7,204.6),material='Metal',color=UTILITY_BLUE,collide=False),
        pipe('IrrigationBranchNorth',(66.5,60.4,208.0),26.0,'x',0.22,UTILITY_BLUE),
        pipe('IrrigationBranchSouth',(66.5,60.4,222.0),26.0,'x',0.22,UTILITY_BLUE),
        part('GrowRailNorth',(29.0,0.32,0.55),(66.5,63.5,208.5),material='Metal',color=STEEL,collide=False),
        part('GrowRailSouth',(29.0,0.32,0.55),(66.5,63.5,221.5),material='Metal',color=STEEL,collide=False),
        part('GrowGlowNorth',(27.5,0.12,0.22),(66.5,63.25,208.5),material='Neon',color=LIGHT_COLD,collide=False,cast_shadow=False,children=[point_light('GrowPoolNorth',LIGHT_COLD,0.8,10.0,True)]),
        part('GrowGlowSouth',(27.5,0.12,0.22),(66.5,63.25,221.5),material='Neon',color=LIGHT_COLD,collide=False,cast_shadow=False,children=[point_light('GrowPoolSouth',LIGHT_COLD,0.8,10.0,True)]),
    ]))
    children.append(model('ProcessorHeroBay',[
        part('ProcessorDeck',(8.5,0.35,7.0),(82.0,56.85,215),material='DiamondPlate',color=STEEL),
        part('RearBackplate',(8.5,5.5,0.35),(82.0,59.5,218.3),material='Metal',color=[0.22,0.27,0.24]),
        part('LeftGuard',(0.35,3.5,6.0),(77.9,58.3,215),material='Metal',color=STEEL_LIGHT),
        asset('ProcessorServiceJunction','junction',(79.0,60.0,218.0),(2.5,2.4,0.95),(0,0,0)),
        asset('ProcessorExhaustVent','vent',(84.7,60.5,218.05),(3.3,2.9,0.58),(0,0,0)),
        asset('ProcessorFeedPipe','rusty_pipe',(85.2,61.8,214.8),(0.46,0.46,6.5),(0,90,0)),
        asset('ProcessorIsolationValve','valve',(85.0,59.2,212.2),(2.5,1.85,1.65),(0,0,0)),
        asset('ProcessedRationCrate','crate',(86.3,58.1,216.2),(3.2,2.3,2.2),(0,-8,0),True),
        part('HazardStripeA',(8.0,0.04,0.28),(82.0,57.05,211.8),material='SmoothPlastic',color=YELLOW,collide=False,cast_shadow=False),
        part('ProcessorLeakStain',(4.0,0.018,2.2),(83.5,57.04,216.7),material='Glass',color=[0.06,0.09,0.075],collide=False,transparency=0.67,rot=(0,-12,0),cast_shadow=False),
        part('TaskLightHousing',(5.0,0.42,1.1),(82.0,63.6,216.8),material='Metal',color=STEEL,collide=False),
        part('TaskLightGlow',(4.4,0.16,0.55),(82.0,63.35,216.8),material='Neon',color=LIGHT_COLD,collide=False,cast_shadow=False,children=[point_light('ProcessorTaskPool',LIGHT_COLD,1.35,11.0,True)]),
        part('ProcessorOverheadFrame',(9.5,0.45,0.65),(82.0,64.0,218.0),material='Metal',color=STEEL_LIGHT),
        part('ProcessorLeftColumn',(0.55,7.0,0.65),(77.5,60.5,218.0),material='Metal',color=[0.20,0.24,0.22]),
        part('ProcessorRightColumn',(0.55,7.0,0.65),(86.5,60.5,218.0),material='Metal',color=[0.20,0.24,0.22]),
        pipe('ProcessorWaterConnection',(78.2,61.4,214.0),5.5,'z',0.28,UTILITY_BLUE),
        pipe('ProcessorWasteReturn',(86.0,58.0,214.0),5.5,'z',0.34,RUST),
        part('ProcessorControlAccent',(2.2,1.2,0.12),(80.5,59.4,218.15),material='Neon',color=LIGHT_WARM,collide=False,cast_shadow=False,children=[point_light('ProcessorWarmAccent',LIGHT_WARM,0.55,5.0,False)]),
        part('ProcessorCanopy',(10.0,0.42,7.0),(82.0,64.4,215.0),material='Metal',color=[0.23,0.27,0.25],collide=False),
        part('CanopyGrowUtilityGlow',(7.0,0.12,0.45),(82.0,64.12,213.0),material='Neon',color=[0.58,0.78,0.68],collide=False,cast_shadow=False,children=[point_light('ProcessorUtilityPool',[0.58,0.78,0.68],1.55,12.0,True)]),
        part('ProcessorDrainChannel',(7.5,0.10,0.8),(82.0,56.96,218.8),material='DiamondPlate',color=STEEL_LIGHT,collide=False),
        part('LocalizedCorrosionWest',(0.08,1.6,2.2),(77.77,57.8,217.95),material='CorrodedMetal',color=RUST,collide=False,transparency=0.15),
    ]))
    children.append(model('SurvivorFarmSupport',[
        asset('SeedSupplyCrate','crate',(54.0,58.0,202.8),(3.4,2.4,2.3),(0,7,0),True),
        asset('ToolSupplyCrate','crate',(58.0,58.0,202.5),(3.2,2.3,2.2),(0,-5,0),True),
        part('ToolRackBack',(6.0,3.4,0.25),(64.5,59.0,202.0),material='Metal',color=STEEL),
        part('ToolRackShelf',(5.6,0.22,1.3),(64.5,58.1,202.5),material='DiamondPlate',color=STEEL_LIGHT),
        pipe('RecoveredWaterHeader',(70.0,62.5,202.3),10.0,'x',0.34,UTILITY_BLUE),
        part('EmergencyFarmLight',(0.5,0.8,0.5),(74.8,61.8,202.3),material='Neon',color=LIGHT_WARM,collide=False,cast_shadow=False,children=[point_light('FarmEmergencyPool',LIGHT_WARM,0.55,7.0,False)]),
        part('WaterTankA',(2.4,4.2,2.4),(77.0,58.9,202.8),material='CorrodedMetal',color=STEEL,shape='Cylinder'),
        part('WaterTankB',(2.0,3.6,2.0),(79.6,58.6,202.8),material='CorrodedMetal',color=STEEL_LIGHT,shape='Cylinder'),
        asset('FarmWaterValve','valve',(76.8,59.2,205.0),(2.2,1.6,1.45),(0,90,0)),
        asset('FarmUtilityJunction','junction',(72.0,59.2,202.1),(2.2,2.1,0.85),(0,0,0)),
    ]))
    return {'ClassName':'Model','attributes':{'EnvironmentPass':'VisibleNewBunkerFarmingRework','PreservesRuntimePlots':True,'PreservesFoodProcessor':True},'Children':children}

OUT.write_text(json.dumps(build(),indent=2)+'\n')
print('generated '+str(OUT))
