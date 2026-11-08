"""Director environment-art rework using accepted GeneratedAssets.

All coordinates are authored in NewBunker staging space and receive ACTIVE_OFFSET
with the rest of NewBunker. Gameplay anchors remain owned by their existing systems.
"""
from __future__ import annotations

from .kit import (AGED_WHITE, CONCRETE_DARK, GREEN, LIGHT_COLD, LIGHT_WARM, RED,
                  RUST, STEEL, STEEL_LIGHT, UTILITY_BLUE, WOOD, YELLOW,
                  cframe, fluorescent, model, part, pipe, point_light, structural_rib)

ASSETS = {
    "valve": ("rbxassetid://75117650394533", (1.9600458,1.3601329,1.2071927),
              {"ColorMap":"rbxassetid://136685065521485","NormalMap":"rbxassetid://78946883212753","RoughnessMap":"rbxassetid://81052079342113","MetalnessMap":"rbxassetid://118332949942821"}),
    "junction": ("rbxassetid://138460865383806", (1.9609708,1.8480989,0.9006205),
                 {"ColorMap":"rbxassetid://139579734340579","NormalMap":"rbxassetid://101009095631637","RoughnessMap":"rbxassetid://73092764580147","MetalnessMap":"rbxassetid://129094780313320"}),
    "vent": ("rbxassetid://129788520191225", (1.9790695,1.7752920,1.9706876),
             {"ColorMap":"rbxassetid://111071233724492","NormalMap":"rbxassetid://101188069065673","RoughnessMap":"rbxassetid://133041917278365","MetalnessMap":"rbxassetid://127496283006416"}),
    "crate": ("rbxassetid://140136727798730", (1.9237564,1.3635647,1.3061225),
              {"ColorMap":"rbxassetid://79418719084559","NormalMap":"rbxassetid://75088026659430","RoughnessMap":"rbxassetid://81827742837440","MetalnessMap":"rbxassetid://72826286691276"}),
    "rusty_pipe": ("rbxassetid://71312017003623", (600.0,200.0,200.0),
                   {"ColorMap":"rbxassetid://112374676768109","NormalMap":"rbxassetid://113503962473805"}),
}

# Published model registrations approved for the environment pass.  The mesh
# and SurfaceAppearance data above remain the verified authoring representation
# used by the existing Rojo model builder.
ASSET_REUSE_IDS = {
    "junction": "97313747351940",
    "valve": "92968150925196",
    "vent": "133282905829866",
    "crate": "110954195423764",
    "rusty_pipe": "127442950110539",
}

def asset(name, kind, pos, target_size, rot=(0,0,0), collide=False):
    mesh_id, _, maps = ASSETS[kind]
    sa={"Name":"SurfaceAppearance","ClassName":"SurfaceAppearance","Properties":maps.copy()}
    return {"Name":name,"ClassName":"MeshPart","Properties":{
        "Anchored":True,"CanCollide":collide,"CanTouch":False,"CanQuery":collide,
        "MeshId":mesh_id,"Size":list(target_size),"CFrame":cframe(pos,rot),"CastShadow":True,
    },"attributes":{
        "EnvironmentAssetKind":kind,
        "RegisteredAssetId":ASSET_REUSE_IDS[kind],
        "WorldScaleNormalized":True,
    },"Children":[sa]}

def _entrance():
    return model("EntranceFirstImpressionRework",[
        model("WestMaintenanceCluster",[
            asset("EmergencyJunctionBox","junction",(-68.0,60.1,15.15),(2.8,2.65,1.28),(0,90,0)),
            pipe("ArmoredFeedUpper",(-65.0,63.2,15.3),6.0,"x",0.30,STEEL_LIGHT),
            pipe("ArmoredFeedDrop",(-68.0,61.9,15.3),2.6,"y",0.30,STEEL_LIGHT),
            asset("IsolationValve","valve",(-67.8,58.0,15.1),(2.8,2.0,1.8),(0,90,0)),
            asset("ReadyAmmoCrate","crate",(-67.3,55.0,17.0),(3.5,2.5,2.4),(0,-8,0),True),
        ]),
        model("EastVentilationStack",[
            asset("IntakeGrille","vent",(-51.0,60.2,17.25),(3.8,3.4,0.65),(0,0,0)),
            part("VentBacking",(4.5,4.1,0.35),(-51.0,60.2,17.58),material="CorrodedMetal",color=STEEL),
            part("CondensationTrack",(0.28,3.0,0.08),(-49.3,57.5,17.35),material="Concrete",color=[0.08,0.12,0.105],collide=False,transparency=0.18),
        ]),
        part("ThresholdWetSheen",(7.0,0.018,3.2),(-60.0,54.025,12.0),material="Glass",color=[0.05,0.075,0.07],collide=False,transparency=0.67,cast_shadow=False),
        part("SurvivorRepairPlate",(4.6,0.16,2.0),(-63.2,54.14,17.7),material="CorrodedMetal",color=RUST,collide=False,rot=(0,12,0)),
        model("AuthoredThresholdDepth",[
            structural_rib("ThresholdRibOuter",-70.0,-50.0,11.0,10.5,depth=0.7),
            structural_rib("ThresholdRibInner",-70.0,-50.0,18.2,10.5,depth=0.65),
            part("WestLowerServicePlinth",(1.0,2.2,7.0),(-69.2,55.1,14.6),material="Concrete",color=CONCRETE_DARK),
            part("EastLowerServicePlinth",(1.0,2.2,7.0),(-50.8,55.1,14.6),material="Concrete",color=CONCRETE_DARK),
            part("OverheadServiceSoffit",(17.0,0.55,2.2),(-60.0,63.8,15.0),material="DiamondPlate",color=STEEL),
            pipe("ThresholdBlueConduit",(-60.0,63.15,16.1),15.5,"x",0.22,UTILITY_BLUE),
            fluorescent("ThresholdPractical",(-60.0,63.2,13.0),LIGHT_WARM,1.75,13),
            part("ExteriorMudTransition",(11.0,0.035,3.0),(-60.0,54.04,8.5),material="Ground",color=[0.16,0.14,0.10],collide=False,transparency=0.08),
        ]),
    ])

def _corridor():
    return model("MajorServiceRunRework",[
        model("ContinuousUtilityRun",[
            asset("ServicePipeSouth","rusty_pipe",(-44.9,63.0,42.0),(0.52,0.52,12.0),(0,90,0)),
            asset("ServicePipeNorth","rusty_pipe",(-44.9,63.0,55.0),(0.52,0.52,12.0),(0,90,0)),
            asset("LineIsolationValve","valve",(-44.7,60.4,49.0),(2.6,1.9,1.7),(0,90,0)),
            asset("ServiceJunctionA","junction",(-45.55,59.1,39.5),(2.5,2.4,1.0),(0,90,0)),
            asset("ServiceJunctionB","junction",(-45.55,59.0,57.2),(2.3,2.2,0.95),(0,90,0)),
            asset("ReturnVent","vent",(-45.52,61.4,52.0),(3.2,2.8,0.62),(0,90,0)),
            part("CableTray",(0.7,0.32,24.0),(-45.15,64.25,48.0),material="Metal",color=STEEL_LIGHT,collide=False),
            part("CableDark",(0.13,0.13,23.0),(-44.85,64.25,48.0),material="SmoothPlastic",color=CONCRETE_DARK,collide=False),
            part("CableBlue",(0.13,0.13,21.5),(-44.65,64.12,48.0),material="SmoothPlastic",color=UTILITY_BLUE,collide=False),
        ]),
        part("DrainageStain",(2.0,0.02,13.0),(-41.0,54.02,51.0),material="Concrete",color=[0.07,0.10,0.09],collide=False,transparency=0.42,rot=(0,2,0),cast_shadow=False),
        part("RemovedPanel",(2.4,0.12,1.6),(-40.3,54.12,57.5),material="CorrodedMetal",color=STEEL_LIGHT,collide=False,rot=(0,-18,0)),
        model("ServiceDepthBays",[
            structural_rib("ServiceRibA",-46.0,-39.0,37.0,10.2,depth=0.55),
            structural_rib("ServiceRibB",-46.0,-39.0,47.0,10.2,depth=0.55),
            structural_rib("ServiceRibC",-46.0,-39.0,58.0,10.2,depth=0.55),
            part("LowerMaintenanceBand",(0.42,2.0,22.0),(-45.72,55.0,48.0),material="Metal",color=[0.20,0.235,0.22],collide=False),
            part("RecessPanelA",(0.20,3.0,4.2),(-45.45,58.0,44.0),material="DiamondPlate",color=CONCRETE_DARK,collide=False),
            part("RecessPanelB",(0.20,3.0,4.2),(-45.45,58.0,55.0),material="DiamondPlate",color=CONCRETE_DARK,collide=False),
            fluorescent("ServicePoolA",(-42.5,63.6,41.5),LIGHT_COLD,1.35,8),
            fluorescent("ServicePoolB",(-42.5,63.6,55.0),LIGHT_COLD,0.65,7),
        ]),
    ])

def _workshop_storage():
    return model("WorkshopStorageRework",[
        model("WorkshopRepairFocal",[
            asset("BenchJunction","junction",(-94.0,60.0,34.0),(2.7,2.55,1.05),(0,90,0)),
            asset("BenchVent","vent",(-95.15,61.4,39.5),(3.0,2.6,0.55),(0,90,0)),
            asset("BenchAirLine","rusty_pipe",(-93.8,63.6,36.8),(0.42,0.42,9.0),(0,90,0)),
            part("HangingLead",(0.14,3.4,0.14),(-91.6,62.0,30.6),material="SmoothPlastic",color=CONCRETE_DARK,collide=False,rot=(0,0,-7)),
        ]),
        model("WorkshopNorthLogisticsAssets",[
            asset("NorthPartsAmmoCrate","crate",(-82.0,55.05,44.15),(2.7,1.9,1.75),(0,-8,0),False),
            part("NorthLogisticsScuff",(4.8,0.018,1.3),(-82.0,54.04,44.35),material="Concrete",color=CONCRETE_DARK,collide=False,transparency=0.45,rot=(0,3,0),cast_shadow=False),
        ]),
        model("WorkshopWestUtilityAssets",[
            asset("WestExtractionValve","valve",(-95.36,59.25,42.3),(0.52,1.55,1.65),(0,90,0),False),
            asset("WestExtractionVent","vent",(-95.36,61.55,44.0),(0.52,2.45,2.75),(0,90,0),False),
            asset("WestExtractionPipe","rusty_pipe",(-95.12,63.6,38.75),(0.40,0.40,8.0),(0,90,0),False),
        ]),
        model("StorageLogisticsCluster",[
            asset("StorageCrateA","crate",(-57.0,55.2,73.5),(3.7,2.6,2.5),(0,-5,0),True),
            asset("StorageCrateB","crate",(-61.0,55.0,74.0),(3.1,2.2,2.2),(0,11,0),True),
            asset("StorageVent","vent",(-67.8,60.5,77.2),(3.4,3.0,0.58),(0,0,0)),
            asset("StorageValve","valve",(-68.0,58.0,74.8),(2.4,1.8,1.6),(0,0,0)),
            part("CartWheelTrackA",(0.22,0.018,8.0),(-61.5,54.02,68.0),material="Concrete",color=CONCRETE_DARK,collide=False,transparency=0.42),
            part("CartWheelTrackB",(0.22,0.018,8.0),(-60.2,54.02,68.0),material="Concrete",color=CONCRETE_DARK,collide=False,transparency=0.42),
            part("StorageRackBack",(7.0,5.4,0.28),(-62.0,57.0,76.9),material="Metal",color=STEEL),
            part("StorageRackDeckA",(6.6,0.24,2.0),(-62.0,55.5,75.9),material="DiamondPlate",color=STEEL_LIGHT),
            part("StorageRackDeckB",(6.6,0.24,2.0),(-62.0,58.0,75.9),material="DiamondPlate",color=STEEL_LIGHT),
            fluorescent("StoragePractical",(-62.0,63.0,72.0),LIGHT_COLD,0.9,9),
        ]),
    ])

def _bedroom():
    return model("BedroomLivingRework",[
        model("ImprovisedLivingUtilities",[
            asset("BedroomVent","vent",(-94.9,61.4,88.0),(3.2,2.8,0.55),(0,90,0)),
            asset("BedroomJunction","junction",(-94.95,58.4,83.0),(2.1,2.0,0.82),(0,90,0)),
            asset("PersonalAmmoBox","crate",(-92.0,54.95,93.2),(2.8,2.0,1.9),(0,-9,0),True),
            asset("HeatPipe","rusty_pipe",(-94.4,63.3,82.5),(0.34,0.34,11.0),(0,90,0)),
            part("DryingLine",(0.08,0.08,8.0),(-86.0,62.4,93.8),material="SmoothPlastic",color=CONCRETE_DARK,collide=False),
            part("HangingBlanket",(3.2,2.7,0.08),(-86.0,60.9,93.75),material="Fabric",color=[0.18,0.23,0.20],collide=False,transparency=0.06),
        ]),
        part("BedsideDampPatch",(4.6,0.018,3.1),(-90.5,54.02,92.5),material="Glass",color=[0.055,0.08,0.072],collide=False,transparency=0.70,rot=(0,-8,0),cast_shadow=False),
        part("BootWearPath",(1.1,0.018,9.0),(-84.5,54.02,82.5),material="Concrete",color=CONCRETE_DARK,collide=False,transparency=0.55,rot=(0,3,0),cast_shadow=False),
        model("HabitationComposition",[
            part("PersonalStorageShelf",(5.4,0.30,1.8),(-92.0,57.0,91.0),material="WoodPlanks",color=WOOD),
            part("PersonalStorageBack",(5.4,3.5,0.22),(-92.0,58.7,91.8),material="Metal",color=STEEL),
            part("BedsideUtilityTable",(2.2,0.35,1.8),(-88.0,56.2,91.5),material="WoodPlanks",color=WOOD),
            part("BedsideLamp",(0.55,0.8,0.55),(-88.0,57.0,91.5),material="Neon",color=LIGHT_WARM,collide=False,cast_shadow=False,children=[point_light("BedsideWarmPool",LIGHT_WARM,1.15,8.0,True)]),
            part("FoldedSupplyBundleA",(2.0,0.45,1.4),(-92.8,57.45,91.0),material="Fabric",color=[0.20,0.24,0.20],collide=False),
            part("FoldedSupplyBundleB",(1.8,0.38,1.2),(-90.5,57.4,91.0),material="Fabric",color=[0.28,0.23,0.18],collide=False),
            part("LivingWallLowerBand",(0.28,2.0,13.0),(-95.55,55.2,84.5),material="Metal",color=[0.21,0.245,0.22],collide=False),
        ]),
    ])

def build_environment_rework():
    return [_entrance(),_corridor(),_workshop_storage(),_bedroom()]
