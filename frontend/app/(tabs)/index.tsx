import Ionicons from '@expo/vector-icons/Ionicons';
import { useState } from "react";
import { FlatList, Pressable, StyleSheet, Text, View } from "react-native";

// Mock data
const CATEGORY = [
  { id: 1, title: 'Transport', amount: 'Total' },
  { id: 2, title: 'Food', amount: 'Total' },
  { id: 3, title: 'Shopping', amount: 'Total' },
  { id: 4, title: 'Housing', amount: 'Total' },
  { id: 5, title: 'Health', amount: 'Total' },
]

// Components // Might be wise to move to a different file altogether
const Item = ({ title, amount, expose }: { title: string, amount: string, expose: boolean }) => (
  <Pressable
    onPress={() => { if (!expose) { console.log("child pressed") } }}
  >
    <View
      style={styles.item}>
      {expose &&
        <Pressable
          style={styles.removeButton}
          onPress={() => console.log("remove pressed")}>
          <Ionicons name="remove-circle" size={30} color="#a90000c1" />
        </Pressable>
      }
      <Text>{title}</Text>
      <Text>{amount}</Text>
    </View>
  </Pressable>
)

export default function Index() {
  // States
  const [exposeMenu, setExposeMenu] = useState(false)

  return (
    <Pressable
      style={styles.container}
      onLongPress={() => {
        console.log("parent press")
        setExposeMenu(prev => !prev)
      }}
    >
      <View>
        <FlatList data={CATEGORY}
          renderItem={({ item }) => <Item title={item.title} amount={item.amount} expose={exposeMenu} />}
          keyExtractor={item => item.id.toString()}
          numColumns={3}
          columnWrapperStyle={styles.row}
        />
      </View>

      <Pressable
        style={styles.addButton}
        onPress={() => console.log("add press")}>
        <Ionicons name="add-circle-sharp" size={60} color="#6495ed" />
      </Pressable>
    </Pressable>
  )
}
const styles = StyleSheet.create({
  container: {
    alignItems: "center",
    backgroundColor: "#ffffff",
    paddingVertical: 20,
    flex: 1,
  },
  row: {
    marginBottom: 10,
    gap: 10,
    justifyContent: "flex-start",
  },
  item: {
    width: 120,
    height: 200,
    gap: 30,
    justifyContent: "flex-end",
    alignItems: "center",
    padding: 5,
    borderRadius: 10,
    backgroundColor: "#6495ed",

  },
  removeButton: {
    position: "absolute",
    top: 0,
    right: 0
  },
  addButton: {
    position: "absolute",
    bottom: 20,
  }
})
