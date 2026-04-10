import { createFileRoute } from "@tanstack/react-router";
import { Editor } from "@/components/PhotoShopee/Editor";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "PhotoShopee - Editor de Imagens" },
      { name: "description", content: "Editor de imagens com manipulação direta de pixels" },
    ],
  }),
});

function Index() {
  return <Editor />;
}
