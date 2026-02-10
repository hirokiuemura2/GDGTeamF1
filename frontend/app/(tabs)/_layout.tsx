import { Tabs } from "expo-router";
import React from "react";
import Ionicons from '@expo/vector-icons/Ionicons';

export default function TabsLayout() {
  return (
    <Tabs>
      <Tabs.Screen name="index" options={{
        title:"Home",
        tabBarIcon: ({ color, size }) => (
          <Ionicons name="home-outline" size={size} color={color} />
        )
      }} />
      <Tabs.Screen name="statistics" options={{
        title: "Statistics",
        tabBarIcon: ({ color, size }) => (
          <Ionicons name="stats-chart-outline" size={24} color={color} />
        )
      }} />
      <Tabs.Screen name="settings" options={{
        title: "Settings",
        tabBarIcon: ({ color, size }) => (
          <Ionicons name="settings-outline" size={size} color={color} />
        )
      }} />
    </Tabs>
  )
}
