import { createApp } from 'vue'
import {
  Button,
  Calendar,
  Cell,
  CellGroup,
  CountDown,
  Divider,
  Field,
  Form,
  NoticeBar,
  Tag,
} from 'vant'
import 'vant/lib/index.css'
import './style.css'
import App from './App.vue'

const app = createApp(App)

app.use(Button)
app.use(Calendar)
app.use(Cell)
app.use(CellGroup)
app.use(CountDown)
app.use(Divider)
app.use(Field)
app.use(Form)
app.use(NoticeBar)
app.use(Tag)

app.mount('#app')
