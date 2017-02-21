/** include the libraries you need in your planner here */
/** for global path planner interface */
#include <string>
#include <ros/ros.h>
#include <costmap_2d/costmap_2d_ros.h>
#include <costmap_2d/costmap_2d.h>
#include <nav_core/base_global_planner.h>
#include <geometry_msgs/PoseStamped.h>
#include <nav_msgs/Path.h>
#include <angles/angles.h>
#include <base_local_planner/world_model.h>
#include <base_local_planner/costmap_model.h>

using std::string;

#ifndef GLOBAL_PLANNER_CPP
#define GLOBAL_PLANNER_CPP

namespace remote_global_planner {
    typedef std::vector<geometry_msgs::PoseStamped> plan_t;
    typedef costmap_2d::Costmap2DROS costmap_t;

    class RemoteGlobalPlanner : public nav_core::BaseGlobalPlanner {
        string name;
        costmap_t* costmap_ros;
        plan_t plan;
        ros::NodeHandle node_handler;
        ros::Subscriber subscriber;
        bool initialized;
    public:
        RemoteGlobalPlanner();
        RemoteGlobalPlanner(string name, costmap_t* costmap_ros);

        /** overridden classes from interface nav_core::BaseGlobalPlanner **/
        void initialize(string name, costmap_t* costmap_ros);
        bool makePlan(const geometry_msgs::PoseStamped& start,
                      const geometry_msgs::PoseStamped& goal,
                      plan_t& plan
        );
        void planCallback(const nav_msgs::Path path);
    };
};
#endif