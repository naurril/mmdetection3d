# dataset settings
dataset_type = 'SuscapeDataset'
data_root = 'data/suscape/'
class_names = ['Car', 'Pedestrian', 'ScooterRider'
               , 'Truck', 'Scooter',
                'Bicycle', 'Van', 'Bus', 'BicycleRider', #'BicycleGroup', 
                'Trimotorcycle', #'RoadWorker', 
                ]

point_cloud_range = [-80, -80, -5, 80, 80, 3]
input_modality = dict(use_lidar=True, use_camera=False)
metainfo = dict(classes=class_names)

# db_sampler = dict(
#     data_root=data_root,
#     info_path=data_root + 'kitti_dbinfos_train.pkl',
#     rate=1.0,
#     prepare=dict(
#         filter_by_difficulty=[-1],
#         filter_by_min_points=dict(Car=5, Pedestrian=10, Cyclist=10)),
#     classes=class_names,
#     sample_groups=dict(Car=12, Pedestrian=6, Cyclist=6),
#     points_loader=dict(
#         type='LoadPointsFromFile', coord_type='LIDAR', load_dim=4, use_dim=4))

train_pipeline = [
    dict(
        type='LoadPointsFromFile',
        coord_type='LIDAR',
        load_dim=4,  # x, y, z, intensity
        use_dim=4),
    dict(type='LoadAnnotations3D', with_bbox_3d=True, with_label_3d=True),
    #dict(type='ObjectSample', db_sampler=db_sampler),
    dict(type='PointsRangeFilter', point_cloud_range=point_cloud_range),
    dict(type='ObjectRangeFilter', point_cloud_range=point_cloud_range),    
    # dict(
    #     type='ObjectNoise',
    #     num_try=100,
    #     translation_std=[1.0, 1.0, 0.5],
    #     global_rot_range=[0.0, 0.0],
    #     rot_range=[-0.78539816, 0.78539816]),
    dict(type='RandomFlip3D', flip_ratio_bev_horizontal=0.5),
    # dict(type='PointSample', num_points=16384, sample_range=None),
    dict(
        type='GlobalRotScaleTrans',
        rot_range=[-0.78539816, 0.78539816],
        scale_ratio_range=[0.95, 1.05]),
    dict(type='PointShuffle'),
    # dict(
    #     type='PointsSave',
    #     path='./temp'
    # ),
    dict(
        type='Pack3DDetInputs',
        keys=['points', 'gt_bboxes_3d', 'gt_labels_3d']),
]
test_pipeline = [
    dict(type='LoadPointsFromFile', coord_type='LIDAR', load_dim=4, use_dim=4),    
    # dict(type='PointSample', num_points=16384, sample_range=None),
    dict(
        type='MultiScaleFlipAug3D',
        img_scale=(1333, 800),
        pts_scale_ratio=1,
        flip=False,
        transforms=[
            dict(
                type='GlobalRotScaleTrans',
                rot_range=[0, 0],
                scale_ratio_range=[1., 1.],
                translation_std=[0, 0, 0]),
            dict(type='RandomFlip3D'),
            dict(
                type='PointsRangeFilter', point_cloud_range=point_cloud_range)
        ]),
    dict(type='Pack3DDetInputs', keys=['points'])
]
# construct a pipeline for data and gt loading in show function
# please keep its loading function consistent with test_pipeline (e.g. client)
eval_pipeline = [
    dict(type='LoadPointsFromFile', coord_type='LIDAR', load_dim=4, use_dim=4),
    # dict(type='PointSample', num_points=16384, sample_range=None),
    dict(
        type='MultiScaleFlipAug3D',
        img_scale=(1333, 800),
        pts_scale_ratio=1,
        flip=False,
        transforms=[
            dict(
                type='GlobalRotScaleTrans',
                rot_range=[0, 0],
                scale_ratio_range=[1., 1.],
                translation_std=[0, 0, 0]),
            dict(type='RandomFlip3D'),
            dict(
                type='PointsRangeFilter', point_cloud_range=point_cloud_range)
        ]),
    dict(type='Pack3DDetInputs', keys=['points'])
]


train_dataloader = dict(
    batch_size=2,
    num_workers=2,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    dataset=dict(
        type='RepeatDataset',
        times=2,
        dataset=dict(
            type=dataset_type,
            data_root=data_root,
            ann_file='suscape_infos_train.pkl',
            data_prefix=dict(pts=''),
            pipeline=train_pipeline,
            modality=input_modality,
            test_mode=False,
            metainfo=metainfo,            
            # we use box_type_3d='LiDAR' in kitti and nuscenes dataset
            # and box_type_3d='Depth' in sunrgbd and scannet dataset.
            box_type_3d='LiDAR')))
val_dataloader = dict(
    batch_size=2,
    num_workers=2,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        data_prefix=dict(pts=''),
        ann_file='suscape_infos_val.pkl',
        pipeline=test_pipeline,
        modality=input_modality,
        test_mode=True,
        metainfo=metainfo,
        box_type_3d='LiDAR'))
test_dataloader = dict(
    batch_size=2,
    num_workers=2,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        data_root=data_root,
        data_prefix=dict(pts=''),
        ann_file='suscape_infos_val.pkl',
        pipeline=test_pipeline,
        modality=input_modality,
        test_mode=True,
        metainfo=metainfo,
        box_type_3d='LiDAR'))
val_evaluator = dict(
    type='SuscapeMetric',
    data_root='./',
    ann_file=data_root + 'suscape_infos_val.pkl',
    jsonfile_prefix='results/suscape-3d/suscape-3d_results'
    )
test_evaluator = val_evaluator

vis_backends = [dict(type='LocalVisBackend')]
visualizer = dict(
    type='Det3DLocalVisualizer', vis_backends=vis_backends, name='visualizer')
