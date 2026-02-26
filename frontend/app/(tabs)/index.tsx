import { FlatList, KeyboardAvoidingView, StyleSheet, Text, View } from "react-native";


const CATEGORY = [
  { id: 1, title: 'Transport', amount: 'Total' },
  { id: 2, title: 'Food', amount: 'Total' },
  { id: 3, title: 'Shopping', amount: 'Total' },
  { id: 4, title: 'Housing', amount: 'Total' },
  { id: 5, title: 'Health', amount: 'Total' },
]

const Item = ({title, amount}: {title: string, amount: string}) => (
  <View style={styles.item}>
    <Text>{title}</Text>
    <Text>{amount}</Text>
  </View>
)

export default function Index() {
  return (
    <KeyboardAvoidingView style={styles.container}>
      <FlatList data={CATEGORY}
      renderItem={({item}) => <Item title={item.title} amount={item.amount}/>}
      keyExtractor={item => item.id.toString()}
      numColumns={3}
      columnWrapperStyle={styles.row}
      />
    </KeyboardAvoidingView >
  )
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: "center",
    backgroundColor: "#ffffff",
    paddingVertical: 50,
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
  title: {

  }
})
