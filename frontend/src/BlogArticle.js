import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const BlogArticle = () => {
  const { slug } = useParams();
  const [article, setArticle] = useState(null);
  const [relatedArticles, setRelatedArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;

  useEffect(() => {
    loadArticle();
  }, [slug]);

  const loadArticle = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Simuler le chargement d'un article pour la démo
      if (slug === 'eau-robinet-dangereuse-sante') {
        setArticle({
          id: '1',
          title: "Pourquoi l'eau du robinet peut être dangereuse pour votre santé",
          content: `# Pourquoi l'eau du robinet peut être dangereuse pour votre santé

L'eau du robinet, bien qu'elle soit traitée et considérée comme potable, peut contenir de nombreux contaminants qui posent des risques pour votre santé. Voici les principales menaces que vous devez connaître.

## 🧪 Les contaminants chimiques

### Chlore et chloramine
Le chlore, utilisé pour désinfecter l'eau, peut former des sous-produits cancérigènes appelés trihalométhanes (THM). Ces composés augmentent les risques de cancer de la vessie et du côlon.

### Métaux lourds
- **Plomb** : Provient des anciennes canalisations, cause des troubles neurologiques
- **Mercure** : Affecte le système nerveux central
- **Cadmium** : Toxique pour les reins et les os

### Pesticides et herbicides
Les résidus agricoles contaminent les nappes phréatiques et se retrouvent dans votre verre. Ces substances sont liées à :
- Troubles endocriniens
- Problèmes de fertilité  
- Risques cancérigènes

## 🦠 Les contaminants biologiques

### Bactéries pathogènes
Malgré la chloration, certaines bactéries résistantes peuvent survivre :
- E. coli
- Salmonelle
- Légionelle

### Parasites
- Cryptosporidium
- Giardia
- Amibes libres

## 💊 Résidus pharmaceutiques

L'eau du robinet contient souvent des traces de :
- Antibiotiques
- Hormones
- Antidépresseurs
- Médicaments contre le cancer

Ces résidus ne sont pas éliminés par les stations d'épuration traditionnelles.

## 🛡️ La solution : l'osmose inverse

L'osmose inverse élimine 99% des contaminants :
- Filtration ultra-fine (0,0001 micron)
- Élimination des métaux lourds
- Suppression des bactéries et virus
- Réduction des produits chimiques

### Nos osmoseurs Josmoze

- **Osmoseur Essentiel (449€)** : Protection familiale efficace
- **Osmoseur Premium (549€)** : Technologie avancée avec reminéralisation
- **Osmoseur Prestige (899€)** : Solution professionnelle haut de gamme

## 📊 Études scientifiques

Selon l'OMS, plus de 2 milliards de personnes n'ont pas accès à une eau vraiment sûre. En France :
- 2,8 millions de personnes consomment une eau non conforme
- 50% des nappes phréatiques sont contaminées par les pesticides

## ⚡ Action immédiate

Ne prenez plus de risques avec votre santé. Testez votre eau et découvrez nos solutions d'osmose inverse adaptées à vos besoins.

*Contactez nos experts pour une analyse gratuite de votre eau.*`,
          category: "Santé",
          featured_image: "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=1200&h=600&fit=crop&q=80",
          published_date: "2024-09-19",
          reading_time: 8,
          view_count: 1251,
          author: "Équipe Josmoze",
          seo_title: "Pourquoi l'eau du robinet peut être dangereuse pour votre santé",
          seo_description: "Découvrez les risques cachés de l'eau du robinet : chlore, métaux lourds, pesticides et micro-organismes qui menacent votre santé au quotidien."
        });
        
        setRelatedArticles([
          {
            id: '2',
            title: "Les 7 bienfaits prouvés des osmoseurs pour votre famille",
            slug: "bienfaits-osmoseurs-famille",
            featured_image: "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=200&fit=crop&q=80",
            category: "Bienfaits"
          },
          {
            id: '3',
            title: "Témoignages clients : Comment l'osmose inverse a changé leur vie",
            slug: "temoignages-clients-osmose-inverse",
            featured_image: "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=400&h=200&fit=crop&q=80",
            category: "Témoignages"
          }
        ]);
      } else {
        // Essayer de charger depuis l'API
        const response = await axios.get(`${backendUrl}/api/blog/articles/${slug}`);
        if (response.data.success) {
          setArticle(response.data.article);
          
          // Charger articles liés
          const relatedResponse = await axios.get(`${backendUrl}/api/blog/articles/${slug}/related`);
          if (relatedResponse.data.success) {
            setRelatedArticles(relatedResponse.data.related_articles);
          }
        }
      }
    } catch (error) {
      console.error('Erreur chargement article:', error);
      setError('Article non trouvé');
    }
    
    setLoading(false);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Santé': 'bg-red-100 text-red-800',
      'Bienfaits': 'bg-green-100 text-green-800',
      'Témoignages': 'bg-blue-100 text-blue-800',
      'Conseils': 'bg-yellow-100 text-yellow-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement de l'article...</p>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">😞</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Article non trouvé</h2>
          <p className="text-gray-600 mb-8">
            L'article que vous recherchez n'existe pas ou a été supprimé.
          </p>
          <Link
            to="/blog"
            className="inline-flex items-center bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            ← Retour au blog
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Image */}
      <div className="relative h-96 overflow-hidden">
        <img
          src={article.featured_image}
          alt={article.title}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black bg-opacity-40"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center text-white max-w-4xl px-4">
            <span className={`inline-block px-4 py-2 rounded-full text-sm font-medium mb-4 ${getCategoryColor(article.category)}`}>
              {article.category}
            </span>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              {article.title}
            </h1>
            <div className="flex items-center justify-center space-x-6 text-white text-opacity-90">
              <span>✍️ {article.author}</span>
              <span>📅 {formatDate(article.published_date)}</span>
              <span>⏱️ {article.reading_time} min de lecture</span>
              <span>👁️ {article.view_count} vues</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-16">
        {/* Breadcrumb */}
        <nav className="mb-8">
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <Link to="/" className="hover:text-blue-600">Accueil</Link>
            <span>›</span>
            <Link to="/blog" className="hover:text-blue-600">Blog</Link>
            <span>›</span>
            <span className="text-gray-900">{article.category}</span>
          </div>
        </nav>

        {/* Article Content */}
        <article className="bg-white rounded-lg shadow-lg p-8 mb-12">
          <div className="prose prose-lg max-w-none">
            <ReactMarkdown
              components={{
                h1: ({children}) => <h1 className="text-3xl font-bold text-gray-900 mb-6">{children}</h1>,
                h2: ({children}) => <h2 className="text-2xl font-bold text-gray-900 mb-4 mt-8">{children}</h2>,
                h3: ({children}) => <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">{children}</h3>,
                p: ({children}) => <p className="text-gray-700 mb-4 leading-relaxed">{children}</p>,
                ul: ({children}) => <ul className="list-disc list-inside mb-4 space-y-2">{children}</ul>,
                li: ({children}) => <li className="text-gray-700">{children}</li>,
                strong: ({children}) => <strong className="font-semibold text-gray-900">{children}</strong>,
                blockquote: ({children}) => (
                  <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-6">
                    {children}
                  </blockquote>
                ),
                table: ({children}) => (
                  <div className="overflow-x-auto my-6">
                    <table className="min-w-full divide-y divide-gray-200">{children}</table>
                  </div>
                ),
                thead: ({children}) => <thead className="bg-gray-50">{children}</thead>,
                th: ({children}) => <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{children}</th>,
                td: ({children}) => <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{children}</td>
              }}
            >
              {article.content}
            </ReactMarkdown>
          </div>

          {/* CTA Section */}
          <div className="mt-12 p-6 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
            <div className="text-center">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                💧 Prêt à purifier votre eau ?
              </h3>
              <p className="text-gray-700 mb-6">
                Découvrez nos osmoseurs Josmoze et offrez à votre famille une eau parfaitement pure
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/#products-section"
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  🛒 Voir nos osmoseurs
                </Link>
                <Link
                  to="/contact"
                  className="bg-white text-blue-600 border-2 border-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
                >
                  📞 Nous contacter
                </Link>
              </div>
            </div>
          </div>
        </article>

        {/* Related Articles */}
        {relatedArticles.length > 0 && (
          <section className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">
              📖 Articles similaires
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              {relatedArticles.map((related) => (
                <Link
                  key={related.id}
                  to={`/blog/${related.slug}`}
                  className="group block bg-gray-50 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
                >
                  <div className="aspect-video overflow-hidden">
                    <img
                      src={related.featured_image}
                      alt={related.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div className="p-4">
                    <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium mb-2 ${getCategoryColor(related.category)}`}>
                      {related.category}
                    </span>
                    <h4 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                      {related.title}
                    </h4>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
};

export default BlogArticle;